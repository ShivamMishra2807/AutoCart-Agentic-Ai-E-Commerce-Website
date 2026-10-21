"""
Customer support: a chat that answers from real data, and tickets with a human handoff.

Rules:
- The chat reuses the existing agents, so answers come from the database, never invented.
- A customer only ever sees their own chats and tickets. Admins/staff see all tickets.
- Details are only saved to a ticket after the customer reviews and agrees (consent=true).
- The assistant hands over to a person when asked, when the customer is upset, or when it cannot help.
"""

import re
import uuid
import datetime
from typing import Any, Dict, List, Optional

from django.utils import timezone
from rest_framework import status as http
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .agents.engine import AgentEngine
from .notify import send_email
from . import agent_graph
from .assistant_memory import first_name, learn, memory_note, personalise

from .models import ChatMessage, ChatSession, Order, SupportTicket, TicketMessage, UserMemory
from .views import get_user_from_token

ADMIN_ROLES = ('ADMIN', 'STAFF')
orchestrator = AgentEngine()

HUMAN_WORDS = [
    'human', 'real person', 'agent', 'representative', 'talk to someone', 'speak to someone', 'manager', 'customer care',
    'insaan', 'kisi se baat', 'baat karni', 'call me',
]
UPSET_WORDS = [
    'angry', 'worst', 'useless', 'fraud', 'scam', 'terrible', 'cheated', 'disgusting', 'pathetic', 'never again',
    'bakwas', 'dhokha', 'bekaar', 'bahut kharab', 'complaint',
]
ORDER_WORDS = [
    'order', 'track', 'delivery', 'deliver', 'return', 'refund', 'cancel', 'shipping', 'policy', 'invoice', 'cart',
    'coupon', 'kab aayega', 'kab tak', 'wapas', 'paisa', 'mera order',
]
CATEGORY_WORDS = {
    'RETURN': ['return', 'refund', 'wapas', 'replace', 'damaged', 'broken', 'wrong item'],
    'ORDER': ['order', 'track', 'delivery', 'late', 'delay', 'cancel', 'kab aayega'],
    'PAYMENT': ['payment', 'charged', 'paisa', 'upi', 'card', 'cash on delivery'],
    'SELLER': ['seller', 'store', 'shop'],
    'PRODUCT': ['product', 'size', 'colour', 'color', 'warranty', 'quality'],
}


def _now():
    return timezone.now()


def _short(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _has(text: str, words) -> bool:
    return any(w in text for w in words)


def _category(text: str) -> str:
    for cat, words in CATEGORY_WORDS.items():
        if _has(text, words):
            return cat
    return 'GENERAL'


def _order_id(text: str) -> str:
    m = re.search(r'\bORD-\d{4}-\d{3,6}\b', text, re.I)
    return m.group(0).upper() if m else ''


def _due(priority: str):
    hours = {'URGENT': 4, 'HIGH': 8, 'NORMAL': 24, 'LOW': 72}.get(priority, 24)
    return _now() + datetime.timedelta(hours=hours)


def _cards(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for p in (result.get('products') or []):
        images = p.get('images') or []
        cards.append({
            'type': 'product', 'id': p.get('id'), 'name': p.get('name'), 'price': p.get('price'),
            'originalPrice': p.get('originalPrice'), 'rating': p.get('rating'), 'stock': p.get('stock'),
            'image': images[0] if images else '',
        })
    for o in (result.get('orders') or [])[:5]:
        cards.append({
            'type': 'order', 'id': o.get('id'), 'status': o.get('status'), 'date': o.get('date'),
            'total': o.get('totalAmount'), 'payment': o.get('paymentStatus'),
        })
    return cards


def _ticket_json(t: SupportTicket, with_messages: bool = False) -> Dict[str, Any]:
    data = {
        'id': t.id, 'subject': t.subject, 'category': t.category, 'orderId': t.orderId, 'status': t.status,
        'priority': t.priority, 'assignedTo': t.assignedTo, 'customerEmail': t.customerEmail, 'customerName': t.customerName,
        'collectedDetails': t.collectedDetails, 'dueAt': t.dueAt, 'createdAt': t.createdAt, 'updatedAt': t.updatedAt,
        'overdue': bool(t.dueAt and t.dueAt < _now() and t.status in ('OPEN', 'IN_PROGRESS')),
    }
    if with_messages:
        data['messages'] = [
            {'id': m.id, 'author': m.author, 'authorName': m.authorName, 'body': m.body, 'createdAt': m.createdAt}
            for m in t.messages.all()
        ]
    return data


def _make_ticket(user, session: Optional[ChatSession], subject: str, category: str, message: str, order_id: str = '',
                 priority: str = 'NORMAL', details: Optional[dict] = None, include_chat: bool = True) -> SupportTicket:
    ticket = SupportTicket.objects.create(
        id=_short('TKT'), session=session, customerEmail=user.email, customerName=user.name, subject=subject[:200],
        category=category, orderId=order_id, priority=priority, collectedDetails=details or {}, dueAt=_due(priority),
    )
    TicketMessage.objects.create(id=_short('tm'), ticket=ticket, author='customer', authorName=user.name, body=message)
    if include_chat and session:  # the person who picks this up reads the whole story, not just the last line
        lines = [f"{'Customer' if m.role == 'user' else 'Assistant'}: {m.content}" for m in list(session.messages.all())[-10:]]
        if lines:
            TicketMessage.objects.create(id=_short('tm'), ticket=ticket, author='assistant', authorName='AutoCart assistant',
                                         body='Recent chat before this ticket:\n' + '\n'.join(lines))
    return ticket


def _session_for(request, user) -> ChatSession:
    sid = str(request.data.get('sessionId') or '').strip()
    session = ChatSession.objects.filter(id=sid).first() if sid else None
    if session and session.userEmail and (not user or session.userEmail.lower() != user.email.lower()):
        session = None  # never continue someone else's chat
    if not session:
        session = ChatSession.objects.create(id=_short('chat'), userEmail=user.email if user else '')
    return session


# ------------------------------------------------------------------- chat --

@api_view(['POST'])
@permission_classes([AllowAny])
def support_chat_view(request):
    message = str(request.data.get('message') or '').strip()
    if not message:
        return Response({'detail': 'Type a message to start.'}, status=http.HTTP_400_BAD_REQUEST)
    user = get_user_from_token(request)
    session = _session_for(request, user)
    ChatMessage.objects.create(id=_short('msg'), session=session, role='user', content=message)
    low = message.lower()

    wants_human = _has(low, HUMAN_WORDS)
    upset = _has(low, UPSET_WORDS)
    escalated, ticket_id = False, ''

    if wants_human or upset:
        if user:
            ticket = _make_ticket(user, session, subject=message[:80] or 'Needs a person', category=_category(low), message=message,
                                  order_id=_order_id(message), priority='URGENT' if upset else 'HIGH')
            escalated, ticket_id = True, ticket.id
            reply = (f"I'm sorry about this. I've passed your chat to our support team as ticket {ticket.id}, with everything we've "
                     f"discussed so you don't have to repeat yourself. A person will reply here and in your tickets list.")
        else:
            reply = "I can bring in a person, but I need to know who you are first. Please sign in and ask again."
        result = {'agent': 'handoff', 'suggestedActions': ['See my tickets', 'Track my order']}
    else:
        # Check order lookup authorization
        is_my_order_lookup = any(w in low for w in ['my order', 'mera order', 'track my order', 'where is my order'])
        is_order_placement = any(phrase in low for phrase in [
            'from this store', 'from store', 'store se', 'order this', 'order now',
            'place order', 'confirm order', 'buy from store', 'order kar', 'order karo',
            'order karna hai', 'buy now', 'buy this', 'buy instead', 'proceed to order',
            'pehle store se', 'store se mangwao', 'store order', 'order from'
        ])
        is_historical_support = _has(low, ['track', 'delivery', 'return', 'refund', 'cancel', 'shipping', 'policy', 'timeline', 'fulfillment']) or (
            'order' in low and any(w in low for w in ['track', 'status', 'where', 'kab', 'history', 'purana', 'delivered', 'past', 'previous'])
        )

        if is_my_order_lookup and not user:
            result = {'agent': 'customer-engagement', 'suggestedActions': ['Sign in'],
                      'reply': 'Please sign in so I can look up your orders. I only ever show you your own.'}
        elif is_historical_support and not is_order_placement and not any(w in low for w in ['under', 'below', 'kurta', 'kurtas', 'earbuds', 'laptop', 'mouse', 'shoes', 'headphone', 'phone', 'piece', 'second', 'first', 'third', 'cheapest', 'sasta', 'compare', 'yes', 'haan', 'store']):
            result = orchestrator.run_customer_engagement_agent(
                query=message, customer_email=user.email if user else '', cart_items=request.data.get('cartItems') or [],
                session_id=session.id)
        else:
            result = orchestrator.run_sathi(
                query=message,
                session_id=session.id,
                customer_email=user.email if user else None,
                cart_items=request.data.get('cartItems') or []
            )
        reply = str(result.get('reply') or "I couldn't find that. Want me to bring in a person?")

    cards = _cards(result)
    order_card = next((c for c in cards if c.get('type') == 'order'), None)
    if order_card and user:
        note = _where_is_my_order(order_card['id'], user)
        if note:
            reply = f"{reply}\n\n{note}"
    learn(user, message)
    reply = personalise(user, reply, session.id + message)
    ChatMessage.objects.create(id=_short('msg'), session=session, role='assistant', content=reply,
                               agent=str(result.get('agent') or ''), cards=cards)
    actions = list(result.get('suggestedActions') or [])
    if not escalated and 'Talk to a person' not in actions:
        actions.append('Talk to a person')
    return Response({
        'sessionId': session.id,
        'reply': reply,
        'agent': result.get('agent', 'sathi'),
        'cards': cards,
        'suggestedActions': actions[:5],
        'escalated': escalated,
        'ticketId': ticket_id,
        'provider': result.get('llmProvider', 'grounded-engine'),
        'buyProductId': result.get('buyProductId', ''),
        'cartAction': result.get('cartAction'),
        'selectedProductId': result.get('selectedProductId', ''),
        'recommendationListId': result.get('recommendationListId', ''),
        'orderedProductIds': result.get('orderedProductIds', []),
        'quantity': result.get('quantity', 1)
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def support_chat_rating_view(request, session_id):
    user = get_user_from_token(request)
    session = ChatSession.objects.filter(id=session_id).first()
    if not session or (session.userEmail and (not user or session.userEmail.lower() != user.email.lower())):
        return Response({'detail': 'Chat not found.'}, status=http.HTTP_404_NOT_FOUND)
    try:
        rating = int(request.data.get('rating'))
    except (TypeError, ValueError):
        rating = 0
    if not 1 <= rating <= 5:
        return Response({'detail': 'Choose a rating from 1 to 5.'}, status=http.HTTP_400_BAD_REQUEST)
    session.rating = rating
    session.save(update_fields=['rating'])
    return Response({'success': True, 'rating': rating})


# ---------------------------------------------------------------- tickets --

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def support_tickets_view(request):
    user = get_user_from_token(request)
    if not user:
        return Response({'detail': 'Please sign in to use support tickets.'}, status=http.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        tickets = SupportTicket.objects.all().order_by('-updatedAt')
        if user.role in ADMIN_ROLES:
            wanted = request.query_params.get('status')
            if wanted:
                tickets = tickets.filter(status=wanted)
        else:
            tickets = tickets.filter(customerEmail__iexact=user.email)
        return Response([_ticket_json(t) for t in tickets[:200]])

    data = request.data
    if data.get('consent') is not True:  # the customer has seen exactly what is saved, and agreed
        return Response({'detail': 'Please confirm that we may save these details to your ticket.'}, status=http.HTTP_400_BAD_REQUEST)
    body = str(data.get('message') or '').strip()
    subject = str(data.get('subject') or '').strip()
    if not body or not subject:
        return Response({'detail': 'Add a short subject and describe what happened.', 'errors': {'subject': 'Required' if not subject else '', 'message': 'Required' if not body else ''}},
                        status=http.HTTP_400_BAD_REQUEST)
    session = ChatSession.objects.filter(id=str(data.get('sessionId') or '')).first()
    if session and session.userEmail and session.userEmail.lower() != user.email.lower():
        session = None
    order_id = str(data.get('orderId') or '').strip().upper()
    category = str(data.get('category') or _category(f"{subject} {body}".lower())).upper()
    ticket = _make_ticket(user, session, subject=subject, category=category, message=body, order_id=order_id,
                          priority=str(data.get('priority') or 'NORMAL').upper(),
                          details={'orderId': order_id, 'preferredContact': str(data.get('preferredContact') or ''), 'category': category})
    return Response(_ticket_json(ticket, with_messages=True), status=http.HTTP_201_CREATED)


def _ticket_for(user, ticket_id):
    t = SupportTicket.objects.filter(id=ticket_id).first()
    if not t:
        return None
    if user.role in ADMIN_ROLES or t.customerEmail.lower() == user.email.lower():
        return t
    return None


@api_view(['GET', 'PATCH'])
@permission_classes([AllowAny])
def support_ticket_detail_view(request, ticket_id):
    user = get_user_from_token(request)
    if not user:
        return Response({'detail': 'Please sign in.'}, status=http.HTTP_401_UNAUTHORIZED)
    ticket = _ticket_for(user, ticket_id)
    if not ticket:
        return Response({'detail': 'Ticket not found.'}, status=http.HTTP_404_NOT_FOUND)
    if request.method == 'PATCH':
        if user.role not in ADMIN_ROLES:
            return Response({'detail': 'Only the support team can change a ticket.'}, status=http.HTTP_403_FORBIDDEN)
        for field, allowed in (('status', [s for s, _ in SupportTicket.STATUS]), ('priority', [p for p, _ in SupportTicket.PRIORITY])):
            val = str(request.data.get(field) or '').upper()
            if val in allowed:
                setattr(ticket, field, val)
        if 'assignedTo' in request.data:
            ticket.assignedTo = str(request.data.get('assignedTo') or '')[:150]
        ticket.save()
    return Response(_ticket_json(ticket, with_messages=True))


@api_view(['POST'])
@permission_classes([AllowAny])
def support_ticket_messages_view(request, ticket_id):
    user = get_user_from_token(request)
    if not user:
        return Response({'detail': 'Please sign in.'}, status=http.HTTP_401_UNAUTHORIZED)
    ticket = _ticket_for(user, ticket_id)
    if not ticket:
        return Response({'detail': 'Ticket not found.'}, status=http.HTTP_404_NOT_FOUND)
    body = str(request.data.get('body') or '').strip()
    if not body:
        return Response({'detail': 'Write a message first.'}, status=http.HTTP_400_BAD_REQUEST)
    staff = user.role in ADMIN_ROLES
    TicketMessage.objects.create(id=_short('tm'), ticket=ticket, author='support' if staff else 'customer', authorName=user.name, body=body)
    ticket.status = 'WAITING_CUSTOMER' if staff else 'OPEN'
    if staff and not ticket.assignedTo:
        ticket.assignedTo = user.name
    ticket.save()
    if staff:
        send_email(ticket.customerEmail, f'Update on your AutoCart ticket {ticket.id}',
                   f'Hi {ticket.customerName.split()[0] if ticket.customerName else "there"},\n\nOur team replied to "{ticket.subject}":\n\n{body}\n\nYou can reply in your tickets on AutoCart.')
    return Response(_ticket_json(ticket, with_messages=True), status=http.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def support_summary_view(request):
    """Numbers for the admin support dashboard."""
    user = get_user_from_token(request)
    if not user or user.role not in ADMIN_ROLES:
        return Response({'detail': 'Only the support team can see this.'}, status=http.HTTP_403_FORBIDDEN)
    tickets = SupportTicket.objects.all()
    ratings = [s.rating for s in ChatSession.objects.exclude(rating=None)]
    return Response({
        'open': tickets.filter(status='OPEN').count(), 'inProgress': tickets.filter(status='IN_PROGRESS').count(),
        'waitingCustomer': tickets.filter(status='WAITING_CUSTOMER').count(), 'resolved': tickets.filter(status__in=['RESOLVED', 'CLOSED']).count(),
        'overdue': tickets.filter(status__in=['OPEN', 'IN_PROGRESS'], dueAt__lt=_now()).count(),
        'chats': ChatSession.objects.count(), 'averageRating': round(sum(ratings) / len(ratings), 2) if ratings else None,
        'ratedChats': len(ratings),
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def support_last_address_view(request):
    """The delivery address from the customer's latest order, so the chat can offer a one-tap re-order. Only their own."""
    user = get_user_from_token(request)
    if not user:
        return Response({'detail': 'Please sign in.'}, status=http.HTTP_401_UNAUTHORIZED)
    order = Order.objects.filter(customerEmail__iexact=user.email).exclude(shippingAddress={}).order_by('-date', '-id').first()
    a = (order.shippingAddress if order else {}) or {}
    if not a.get('addressLine'):
        return Response({'address': None})
    keep = ('fullName', 'phone', 'addressLine', 'city', 'state', 'pinCode', 'latitude', 'longitude')
    return Response({'address': {**{k: a[k] for k in keep if k in a}, 'fulfillment': 'delivery'}})


def _where_is_my_order(order_id, user):
    """A plain sentence on where the customer's own order is now: which store, how far, and what step it is at."""
    from .seller_orders import _km, drop_point, order_pickup
    order = Order.objects.filter(id=order_id, customerEmail__iexact=user.email).first()
    if not order:
        return ''
    pickup, drop = order_pickup(order), drop_point(order)
    step = {'Packed': 'It has been packed and is ready to leave the store.', 'Confirmed': 'The seller is getting it ready.', 'Pending': 'It is waiting for payment or the seller to confirm.',
            'Delivered': 'It has been delivered.', 'Cancelled': 'It was cancelled.'}.get(order.status, f'Status: {order.status}.')
    where = ''
    if pickup:
        where = f" It is with {pickup['name']}"
        if drop:
            where += f", about {_km((pickup['lat'], pickup['lng']), (drop['lat'], drop['lng'])):.1f} km from your delivery address"
        where += '.'
    return f"{step}{where} Tap the order below to see the route on the map."
