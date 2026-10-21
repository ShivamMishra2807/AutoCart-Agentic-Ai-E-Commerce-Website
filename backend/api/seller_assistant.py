"""
Seller assistant: a seller asks about their own products and orders and gets a structured
answer built only from rows in the database (no LLM, so it is instant, free and cannot invent data).
It only ever sees the signed-in seller's own products and the orders that contain them.
"""

import re

from rest_framework import status as http
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

import json

from .agents.llm_provider import UnifiedLLMProvider
from .models import Enquiry, Order, Product
from .seller_analytics import analytics
from .role_views import LOW_STOCK, _seller_or_error

EXAMPLES = [
    'Which of my products are low on stock?',
    'What are my best selling products?',
    'How many orders are waiting?',
    'What is my revenue so far?',
    'Which products have the best ratings?',
    'Are any customer questions waiting?',
    'What is my profit?',
]


def _has(text, *words):
    return any(w in text for w in words)


def _sales(products):
    """Units and revenue per product id, from non-cancelled orders."""
    ids = {p.id for p in products}
    units, money = {}, {}
    orders = []
    for o in Order.objects.exclude(status='Cancelled'):
        mine = [i for i in (o.items or []) if str(i.get('id')) in ids]
        if not mine:
            continue
        orders.append(o)
        for i in mine:
            pid = str(i.get('id'))
            q = int(i.get('quantity') or 0)
            units[pid] = units.get(pid, 0) + q
            money[pid] = money.get(pid, 0) + q * float(i.get('price') or 0)
    return units, money, orders


def answer(company, message):
    text = (message or '').lower().strip()
    products = list(Product.objects.filter(seller=company))
    if not products:
        return {'answer': 'You have no products listed yet.', 'rows': [], 'columns': []}
    units, money, orders = _sales(products)

    # A product named in the question wins over everything else.
    named = [p for p in products if p.name.lower() in text or (len(text) > 4 and any(w in p.name.lower() for w in re.findall(r'[a-z0-9]{5,}', text)))]
    if named and not _has(text, 'low', 'best', 'revenue', 'waiting'):
        p = named[0]
        return {'answer': f"{p.name}: price ₹{p.price:,.0f}, {p.stock} in stock, rated {p.rating:.1f} from {p.reviewCount} reviews, {units.get(p.id, 0)} sold through AutoCart.",
                'columns': ['Price', 'Stock', 'Rating', 'Sold'], 'rows': [[f'₹{p.price:,.0f}', p.stock, f'{p.rating:.1f}', units.get(p.id, 0)]]}

    if _has(text, 'low', 'stock', 'restock', 'running out', 'almost'):
        low = sorted([p for p in products if p.stock <= LOW_STOCK], key=lambda p: p.stock)
        if not low:
            return {'answer': f'All {len(products)} products have more than {LOW_STOCK} in stock.', 'columns': [], 'rows': []}
        return {'answer': f'{len(low)} product(s) need restocking. Start with {low[0].name} ({low[0].stock} left).',
                'columns': ['Product', 'In stock'], 'rows': [[p.name, p.stock] for p in low[:8]]}
    if _has(text, 'best sell', 'top sell', 'most sold', 'selling'):
        ranked = sorted(products, key=lambda p: units.get(p.id, 0), reverse=True)
        ranked = [p for p in ranked if units.get(p.id, 0)] or []
        if not ranked:
            return {'answer': 'No orders contain your products yet, so there is no sales ranking to show.', 'columns': [], 'rows': []}
        return {'answer': f'{ranked[0].name} is your best seller with {units[ranked[0].id]} unit(s) sold.',
                'columns': ['Product', 'Units sold', 'Revenue'], 'rows': [[p.name, units[p.id], f'₹{money[p.id]:,.0f}'] for p in ranked[:8]]}
    if _has(text, 'profit', 'margin', 'make money', 'made money'):
        a = analytics(products)
        e, pr = a['earnings'], a['profit']
        if pr['costKnown']:
            msg = f"Profit so far is ₹{pr['amount']:,.0f}: sales minus AutoCart commission minus what your products cost you."
            if pr['productsWithoutCost']:
                msg += f" This leaves out {len(pr['productsWithoutCost'])} product(s) where you have not entered a cost price."
        else:
            msg = f"After AutoCart's commission you keep ₹{e['youKeep']:,.0f} from ₹{e['gross']:,.0f} of sales. To see true profit, enter what each product costs you in the Your products list (Cost price)."
        return {'answer': msg, 'columns': ['Sold', 'Commission', 'You keep'], 'rows': [[f"₹{e['gross']:,.0f}", f"₹{e['commission']:,.0f}", f"₹{e['youKeep']:,.0f}"]]}
    if _has(text, 'revenue', 'earn', 'income', 'sales so far'):
        total = sum(money.values())
        return {'answer': f'₹{total:,.0f} from {sum(units.values())} unit(s) across {len(orders)} order(s). This is the item total, before delivery fees and payment charges.', 'columns': [], 'rows': []}
    if _has(text, 'order', 'waiting', 'pending', 'ship'):
        open_orders = [o for o in orders if o.status not in ('Delivered', 'Cancelled', 'Returned')]
        return {'answer': f'{len(open_orders)} order(s) still open out of {len(orders)}.',
                'columns': ['Order', 'Status', 'Date'], 'rows': [[o.id, o.status, o.date] for o in open_orders[:8]]}
    if _has(text, 'rating', 'rated', 'review'):
        ranked = sorted(products, key=lambda p: (p.rating, p.reviewCount), reverse=True)[:5]
        return {'answer': f'{ranked[0].name} has your best rating ({ranked[0].rating:.1f}).',
                'columns': ['Product', 'Rating', 'Reviews'], 'rows': [[p.name, f'{p.rating:.1f}', p.reviewCount] for p in ranked]}
    if _has(text, 'question', 'enquir', 'ask'):
        n = Enquiry.objects.filter(sellerName=company, status='OPEN').count()
        return {'answer': f'{n} customer question(s) waiting. Answer them from the Questions section.' if n else 'No customer questions are waiting.', 'columns': [], 'rows': []}
    if _has(text, 'how many', 'products', 'listed', 'catalog'):
        return {'answer': f'You have {len(products)} products listed.', 'columns': [], 'rows': []}
    return {'answer': "I can answer questions about your stock, sales, orders, ratings and customer questions, or any product by name. Try one of the examples.", 'columns': [], 'rows': []}


SYSTEM = (
    "You are Munim, the AutoCart seller's shop-keeping assistant (munim means the traditional shop accountant). "
    "Answer the seller's question using ONLY the FACTS JSON. Use rupees (₹). Be specific: name products and numbers. "
    "Keep it under 70 words, warm and practical, and end with one concrete next step when useful. "
    "If the facts do not contain the answer, say so plainly. Never invent figures, customers or products."
)
_llm = UnifiedLLMProvider()


def _facts(company, products):
    a = analytics(products)
    last7 = a['salesByDay'][-7:]
    return {
        'shop': company,
        'products': [{'name': p.name, 'category': p.category, 'price': p.price, 'stock': p.stock, 'rating': p.rating, 'reviews': p.reviewCount} for p in products[:40]],
        'last30DaysRevenue': sum(d['revenue'] for d in a['salesByDay']), 'last7DaysRevenue': sum(d['revenue'] for d in last7),
        'topProducts': a['topProducts'], 'categoryMix': a['categoryMix'], 'earnings': a['earnings'], 'profit': a['profit'],
        'openQuestions': Enquiry.objects.filter(sellerName=company, status='OPEN').count(),
    }


def smart_answer(company, first, message):
    """Rules compute the table; Gemini (when available) words the reply from the same facts."""
    base = answer(company, message)
    products = list(Product.objects.filter(seller=company))
    if not products or not _llm.is_configured:
        return {**base, 'provider': 'database'}
    facts = json.dumps(_facts(company, products), default=str)
    try:
        from .langchain_module import get_munim_lcel_chain
        chain = get_munim_lcel_chain()
        out_text = chain.invoke({
            'seller_name': first or 'Seller',
            'facts': facts,
            'question': message
        })
        if out_text and out_text.strip():
            prov = 'groq' if _llm.groq.is_configured else 'google-gemini'
            return {**base, 'answer': out_text.strip(), 'provider': prov}
    except Exception as e:
        logger.warning("Munim LangChain LCEL chain error, falling back: %s", e)
    prompt = f"Seller first name: {first}\nFACTS: {facts}\nQUESTION: {message}"
    out = _llm.generate(SYSTEM, prompt, 0.3, 400)
    if out.get('text'):
        return {**base, 'answer': out['text'].strip(), 'provider': out['provider']}
    return {**base, 'provider': 'database'}


@api_view(['POST'])
@permission_classes([AllowAny])
def seller_assistant_view(request):
    user, company, err = _seller_or_error(request)
    if err:
        return err
    message = str(request.data.get('message', ''))[:300]
    if not message.strip():
        return Response({'detail': 'Please type a question.'}, status=http.HTTP_400_BAD_REQUEST)
    first = (user.name or '').split()[0]
    return Response({**smart_answer(company, first, message), 'examples': EXAMPLES, 'assistant': 'Munim',
                     'source': 'Your products and orders in the AutoCart database'})
