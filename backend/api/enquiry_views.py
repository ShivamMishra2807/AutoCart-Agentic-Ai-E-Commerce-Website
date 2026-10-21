"""
Customer enquiries: ask about a product (answered by the seller or the team) or send a general question.

- Anyone can ask. A guest gives a name and email; a signed-in customer's details are filled in for them.
- Only the person who sells the product (or an admin) can answer it.
- A public answer appears on the product page with the asker's first name only. Emails and phones are never shown.
"""

import re
import uuid

from django.db.models import Q
from django.utils import timezone
from rest_framework import status as http
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .notify import send_email
from .models import Enquiry, Product, SellerApplication
from .views import get_user_from_token

ADMIN_ROLES = ('ADMIN', 'STAFF')
EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


class EnquiryThrottle(AnonRateThrottle):
    rate = '60/hour'  # stops someone flooding the form


def _json(e: Enquiry):
    return {
        'id': e.id, 'productId': e.productId, 'productName': e.productName, 'sellerName': e.sellerName, 'message': e.message,
        'status': e.status, 'answer': e.answer, 'answeredBy': e.answeredBy, 'answeredAt': e.answeredAt, 'isPublic': e.isPublic,
        'createdAt': e.createdAt, 'customerName': e.customerName, 'customerEmail': e.customerEmail, 'customerPhone': e.customerPhone,
    }


def _seller_names(user):
    """Business names this user is an approved seller for."""
    return list(SellerApplication.objects.filter(ownerUserId=user.id, status='APPROVED').values_list('companyName', flat=True))


def _can_answer(user, enq: Enquiry) -> bool:
    if user.role in ADMIN_ROLES:
        return True
    return bool(enq.sellerName) and enq.sellerName in _seller_names(user)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@throttle_classes([EnquiryThrottle])
def enquiries_view(request):
    user = get_user_from_token(request)

    if request.method == 'GET':
        if not user:
            return Response({'detail': 'Please sign in to see enquiries.'}, status=http.HTTP_401_UNAUTHORIZED)
        rows = Enquiry.objects.all()
        if user.role in ADMIN_ROLES:
            wanted = request.query_params.get('status')
            if wanted:
                rows = rows.filter(status=wanted)
        else:  # a customer sees their own; a seller also sees questions about their products
            rows = rows.filter(Q(customerEmail__iexact=user.email) | Q(sellerName__in=_seller_names(user)))
        return Response([_json(e) for e in rows[:200]])

    data = request.data
    message = str(data.get('message') or '').strip()
    name = (user.name if user else str(data.get('name') or '')).strip()
    email = (user.email if user else str(data.get('email') or '')).strip().lower()
    errors = {}
    if len(message) < 10:
        errors['message'] = 'Tell us a little more (at least 10 characters).'
    if len(message) > 2000:
        errors['message'] = 'Please keep it under 2000 characters.'
    if not name:
        errors['name'] = 'Enter your name.'
    if not EMAIL_RE.match(email):
        errors['email'] = 'Enter a valid email so we can reply.'
    if errors:
        return Response({'detail': 'Please fix the highlighted fields.', 'errors': errors}, status=http.HTTP_400_BAD_REQUEST)

    product = Product.objects.filter(id=str(data.get('productId'))).first() if data.get('productId') else None
    enq = Enquiry.objects.create(
        id=f"ENQ-{uuid.uuid4().hex[:8].upper()}", productId=product.id if product else '', productName=product.name if product else '',
        sellerName=product.seller if product else '', customerName=name[:150], customerEmail=email,
        customerPhone=str(data.get('phone') or '')[:30], message=message,
    )
    return Response(_json(enq), status=http.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def enquiry_answer_view(request, enquiry_id):
    user = get_user_from_token(request)
    if not user:
        return Response({'detail': 'Please sign in.'}, status=http.HTTP_401_UNAUTHORIZED)
    enq = Enquiry.objects.filter(id=enquiry_id).first()
    if not enq or not _can_answer(user, enq):
        return Response({'detail': 'Enquiry not found.'}, status=http.HTTP_404_NOT_FOUND)
    answer = str(request.data.get('answer') or '').strip()
    if not answer:
        return Response({'detail': 'Write an answer first.', 'errors': {'answer': 'Required'}}, status=http.HTTP_400_BAD_REQUEST)
    enq.answer, enq.answeredBy, enq.answeredAt, enq.status = answer, user.name, timezone.now(), 'ANSWERED'
    enq.isPublic = bool(request.data.get('isPublic', True)) and bool(enq.productId)
    enq.save()
    send_email(enq.customerEmail, f"Your question to AutoCart: {enq.productName or 'general enquiry'}",
               f"Hi {enq.customerName.split()[0]},\n\nYou asked: {enq.message}\n\nAnswer from {user.name}:\n{answer}\n\nThank you for shopping with AutoCart.")
    return Response(_json(enq))


@api_view(['GET'])
@permission_classes([AllowAny])
def product_questions_view(request, product_id):
    """Answered, public questions for one product. First names only."""
    rows = Enquiry.objects.filter(productId=product_id, status='ANSWERED', isPublic=True)[:30]
    return Response([
        {'id': e.id, 'question': e.message, 'asker': (e.customerName.split() or ['A customer'])[0], 'answer': e.answer,
         'answeredBy': e.answeredBy, 'answeredAt': e.answeredAt}
        for e in rows
    ])
