"""
Role-specific data. Each person only ever gets their own view:

- A seller sees their own products, the orders that contain them, and the questions about them. Nothing about other sellers or the admin side.
- An admin sees marketplace-wide numbers and a plain-language briefing of what needs attention.
- A customer gets neither (403).

The "briefing" and the answer drafts are rule-based and only use data in the database, so they are fast, free and never make things up.
"""

import datetime
import re

from django.db.models import Q
from django.utils import timezone
from rest_framework import status as http
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .seller_analytics import analytics
from .product_images import save_photo
from .stock_rules import history as stock_history
from .models import Payment, StockLog, Enquiry, Order, Payment, Product, SellerApplication, SupportTicket
from .views import get_user_from_token

ADMIN_ROLES = ('ADMIN', 'STAFF')
LOW_STOCK = 10


def _company(user):
    app = SellerApplication.objects.filter(ownerUserId=user.id, status='APPROVED').first()
    return app.companyName if app else ''


def _seller_or_error(request):
    user = get_user_from_token(request)
    if not user:
        return None, None, Response({'detail': 'Please sign in.'}, status=http.HTTP_401_UNAUTHORIZED)
    if user.role != 'SELLER':
        return None, None, Response({'detail': 'This area is for approved sellers.'}, status=http.HTTP_403_FORBIDDEN)
    company = _company(user)
    if not company:
        return None, None, Response({'detail': 'Your seller account is not active yet.'}, status=http.HTTP_403_FORBIDDEN)
    return user, company, None


@api_view(['GET'])
@permission_classes([AllowAny])
def seller_overview_view(request):
    user, company, err = _seller_or_error(request)
    if err:
        return err
    products = list(Product.objects.filter(seller=company).order_by('-reviewCount'))
    ids = {p.id for p in products}
    by_id = {p.id: p for p in products}

    orders, revenue, units = [], 0.0, 0
    for o in Order.objects.exclude(status='Cancelled').order_by('-date', '-id'):
        mine = [i for i in (o.items or []) if str(i.get('id')) in ids]
        if not mine:
            continue
        share = sum(float(i.get('price') or 0) * int(i.get('quantity') or 0) for i in mine)
        revenue += share
        units += sum(int(i.get('quantity') or 0) for i in mine)
        orders.append({'id': o.id, 'date': o.date, 'status': o.status, 'paymentStatus': o.paymentStatus, 'paymentMethod': o.paymentMethod,
                       'customerFirstName': (o.customerName or 'Customer').split()[0], 'items': [{'name': i.get('name'), 'quantity': i.get('quantity')} for i in mine],
                       'yourShare': round(share), 'canPack': o.status in ('Confirmed', 'Processing', 'Pending', 'Order Placed') and not (o.paymentMethod == 'UPI (Scan & Pay)' and o.paymentStatus != 'Paid'),
                       'utr': (Payment.objects.filter(orderId=o.id, provider='upi').exclude(status='FAILED').values_list('providerPaymentId', flat=True).first() or ''), 'pickup': bool((o.shippingAddress or {}).get('storeName')) and not (o.shippingAddress or {}).get('addressLine')})

    open_questions = Enquiry.objects.filter(sellerName=company, status='OPEN').count()
    low = [p for p in products if 0 < p.stock <= LOW_STOCK]
    out = [p for p in products if p.stock <= 0]
    tips = []
    if out:
        tips.append({'level': 'warn', 'text': f"{len(out)} of your products are out of stock, so shoppers cannot buy them: {', '.join(p.name for p in out[:2])}."})
    if low:
        tips.append({'level': 'warn', 'text': f"{len(low)} products are almost gone. Restock {low[0].name} first ({low[0].stock} left)."})
    if open_questions:
        tips.append({'level': 'info', 'text': f"{open_questions} customer question{'s' if open_questions > 1 else ''} waiting. Quick answers help people decide."})
    if not tips:
        tips.append({'level': 'good', 'text': 'Everything looks healthy. Stock is fine and no questions are waiting.'})

    return Response({
        **analytics(products),
        'company': company, 'productsCount': len(products), 'outOfStock': len(out), 'lowStock': len(low), 'openQuestions': open_questions,
        'ordersCount': len(orders), 'unitsSold': units, 'revenue': round(revenue), 'tips': tips, 'orders': orders[:25],
        'products': [{'id': p.id, 'name': p.name, 'price': p.price, 'originalPrice': p.originalPrice, 'stock': p.stock, 'rating': p.rating,
                      'reviewCount': p.reviewCount, 'image': (p.images or [''])[0], 'category': p.category,
                      'autoRestock': p.autoRestock, 'reorderLevel': p.reorderLevel, 'restockQty': p.restockQty, 'costPrice': p.costPrice} for p in products],
    })


@api_view(['PATCH'])
@permission_classes([AllowAny])
def seller_product_update_view(request, product_id):
    """A seller can change the price, stock, auto-restock rule and photo of their own products, and nothing else."""
    user, company, err = _seller_or_error(request)
    if err:
        return err
    product = Product.objects.filter(id=product_id, seller=company).first()
    if not product:
        return Response({'detail': 'Product not found.'}, status=http.HTTP_404_NOT_FOUND)
    errors = {}
    old_stock = product.stock
    if 'price' in request.data:
        try:
            price = float(request.data['price'])
            if price <= 0:
                raise ValueError
            product.price = price
        except (TypeError, ValueError):
            errors['price'] = 'Enter a price above 0.'
    if 'stock' in request.data:
        try:
            stock = int(request.data['stock'])
            if stock < 0 or stock > 100000:
                raise ValueError
            product.stock = stock
        except (TypeError, ValueError):
            errors['stock'] = 'Enter a whole number, 0 or more.'
    if 'costPrice' in request.data:
        try:
            cost = float(request.data['costPrice'] or 0)
            if cost < 0:
                raise ValueError
            product.costPrice = cost
        except (TypeError, ValueError):
            errors['costPrice'] = 'Enter what one unit costs you, 0 or more.'
    if 'autoRestock' in request.data:
        product.autoRestock = str(request.data['autoRestock']).lower() in ('true', '1', 'yes', 'on')
    for key, lo, hi, msg in (('reorderLevel', 0, 100000, 'Enter a whole number, 0 or more.'), ('restockQty', 1, 100000, 'Enter a whole number, 1 or more.')):
        if key in request.data:
            try:
                val = int(request.data[key])
                if not lo <= val <= hi:
                    raise ValueError
                setattr(product, key, val)
            except (TypeError, ValueError):
                errors[key] = msg
    photo = request.FILES.get('image')
    if photo and not errors:
        url, problem = save_photo(photo, request)
        if problem:
            errors['image'] = problem
        else:
            product.images = [url] + [i for i in (product.images or []) if i != url][:5]
    if errors:
        return Response({'detail': 'Please fix the highlighted fields.', 'errors': errors}, status=http.HTTP_400_BAD_REQUEST)
    if product.originalPrice and product.originalPrice > product.price:
        product.discount = round((1 - product.price / product.originalPrice) * 100)
    else:
        product.discount = 0
    product.stockStatus = 'Out of Stock' if product.stock <= 0 else ('Low Stock' if product.stock <= LOW_STOCK else 'In Stock')
    product.save()
    if product.stock != old_stock:
        StockLog.objects.create(productId=product.id, change=product.stock - old_stock, stockAfter=product.stock, reason='manual', by=user.email)
    return Response({'id': product.id, 'price': product.price, 'stock': product.stock, 'discount': product.discount, 'stockStatus': product.stockStatus,
                     'autoRestock': product.autoRestock, 'reorderLevel': product.reorderLevel, 'restockQty': product.restockQty, 'costPrice': product.costPrice, 'image': (product.images or [''])[0]})


@api_view(['GET'])
@permission_classes([AllowAny])
def seller_stock_log_view(request, product_id):
    """The history of one product's stock: sales, manual edits and auto-restocks."""
    user, company, err = _seller_or_error(request)
    if err:
        return err
    if not Product.objects.filter(id=product_id, seller=company).exists():
        return Response({'detail': 'Product not found.'}, status=http.HTTP_404_NOT_FOUND)
    return Response({'history': stock_history(product_id)})


@api_view(['GET'])
@permission_classes([AllowAny])
def admin_overview_view(request):
    user = get_user_from_token(request)
    if not user or user.role not in ADMIN_ROLES:
        return Response({'detail': 'Only an administrator can see this.'}, status=http.HTTP_403_FORBIDDEN)
    now = timezone.now()
    review_q = SellerApplication.objects.filter(status__in=['PENDING_ADMIN_APPROVAL', 'NEEDS_MANUAL_REVIEW'])
    riskiest = review_q.order_by('-riskScore').first()
    tickets_open = SupportTicket.objects.filter(status__in=['OPEN', 'IN_PROGRESS'])
    overdue = tickets_open.filter(dueAt__lt=now).count()
    enquiries = Enquiry.objects.filter(status='OPEN').count()
    awaiting = Order.objects.filter(paymentStatus='Awaiting Payment').count()
    failed = Payment.objects.filter(status='FAILED', createdAt__gte=now - datetime.timedelta(days=7)).count()
    low = Product.objects.filter(stock__gt=0, stock__lte=LOW_STOCK)
    out = Product.objects.filter(stock__lte=0).count()
    today = datetime.date.today().isoformat()
    today_orders = Order.objects.filter(date=today).exclude(status='Cancelled')
    today_revenue = sum(o.totalAmount for o in today_orders)

    units = {}
    for o in Order.objects.exclude(status='Cancelled'):
        for i in o.items or []:
            units[i.get('name')] = units.get(i.get('name'), 0) + int(i.get('quantity') or 0)
    top = max(units.items(), key=lambda kv: kv[1]) if units else None

    briefing = []
    if review_q.count():
        extra = f" The riskiest is {riskiest.companyName} (risk {riskiest.riskScore}/100)." if riskiest else ''
        briefing.append({'level': 'warn', 'text': f"{review_q.count()} seller application{'s' if review_q.count() > 1 else ''} waiting for your decision.{extra}", 'link': '/admin/ai-seller-onboarding'})
    if overdue:
        briefing.append({'level': 'bad', 'text': f"{overdue} support ticket{'s are' if overdue > 1 else ' is'} past the reply deadline. Customers are waiting.", 'link': '/admin/support'})
    elif tickets_open.count():
        briefing.append({'level': 'info', 'text': f"{tickets_open.count()} support ticket{'s' if tickets_open.count() > 1 else ''} open, none overdue.", 'link': '/admin/support'})
    if enquiries:
        briefing.append({'level': 'info', 'text': f"{enquiries} customer question{'s' if enquiries > 1 else ''} not answered yet.", 'link': '/admin/enquiries'})
    if failed or awaiting:
        briefing.append({'level': 'warn', 'text': f"{awaiting} order{'s' if awaiting != 1 else ''} waiting for online payment and {failed} failed payment{'s' if failed != 1 else ''} in the last 7 days.", 'link': '/admin/payments'})
    if low.count() or out:
        names = ', '.join(p.name for p in low.order_by('stock')[:2])
        briefing.append({'level': 'warn', 'text': f"{out} product{'s' if out != 1 else ''} out of stock and {low.count()} almost gone{(': ' + names) if names else ''}.", 'link': '/admin/inventory'})
    if today_orders.count():
        briefing.append({'level': 'good', 'text': f"{today_orders.count()} order{'s' if today_orders.count() > 1 else ''} today worth ₹{round(today_revenue):,}."})
    if top:
        briefing.append({'level': 'good', 'text': f"Best seller so far: {top[0]} ({top[1]} sold)."})
    if not briefing:
        briefing.append({'level': 'good', 'text': 'Nothing needs attention right now.'})

    return Response({
        'cards': {'applications': review_q.count(), 'openTickets': tickets_open.count(), 'overdueTickets': overdue, 'openEnquiries': enquiries,
                  'awaitingPayment': awaiting, 'lowStock': low.count(), 'outOfStock': out, 'ordersToday': today_orders.count()},
        'briefing': briefing,
        'applications': [{
            'id': ap.id, 'company': ap.companyName, 'applicant': ap.applicantName, 'city': ap.city, 'status': ap.status,
            'riskScore': ap.riskScore, 'riskCategory': ap.riskCategory, 'trustScore': max(0, 100 - ap.riskScore),
            'documents': ap.documents.count(), 'submitted': ap.createdAt.date().isoformat(),
            'reasons': [c['label'] for c in (ap.verificationResults or {}).get('checks', []) if c.get('status') in ('mismatch', 'missing')][:3],
        } for ap in review_q.order_by('-riskScore')[:8]],
    })


def _tokens(text: str):
    return set(re.findall(r'[a-z0-9]{3,}', (text or '').lower()))


@api_view(['POST'])
@permission_classes([AllowAny])
def enquiry_draft_view(request, enquiry_id):
    """Suggests an answer from the product's own details. The seller reads it, edits it and decides whether to send it."""
    user = get_user_from_token(request)
    if not user:
        return Response({'detail': 'Please sign in.'}, status=http.HTTP_401_UNAUTHORIZED)
    enq = Enquiry.objects.filter(id=enquiry_id).first()
    allowed = enq and (user.role in ADMIN_ROLES or (user.role == 'SELLER' and enq.sellerName and enq.sellerName == _company(user)))
    if not allowed:
        return Response({'detail': 'Enquiry not found.'}, status=http.HTTP_404_NOT_FOUND)
    product = Product.objects.filter(id=enq.productId).first()
    if not product:
        return Response({'draft': 'Thanks for getting in touch. ', 'basis': [], 'confidence': 'low',
                         'note': 'This is a general question, so there is no product to draw facts from. Write the answer yourself.'})

    q = _tokens(enq.message)
    facts, basis = [], []
    for key, value in (product.specifications or {}).items():
        if q & (_tokens(key) | _tokens(str(value))):
            facts.append(f'{key}: {value}'); basis.append(key)
    if q & {'stock', 'available', 'availability', 'have'}:
        facts.append(f"We have {product.stock} in stock right now." if product.stock > 0 else 'It is out of stock at the moment.'); basis.append('stock')
    if q & {'price', 'cost', 'discount', 'offer'}:
        facts.append(f"The price is ₹{product.price:,.0f}" + (f" (was ₹{product.originalPrice:,.0f})." if product.originalPrice > product.price else '.')); basis.append('price')
    if q & {'return', 'refund', 'replace', 'replacement'}:
        facts.append('Returns are accepted for 7 days after delivery.'); basis.append('returns')
    if q & {'cash', 'cod', 'pay', 'payment'}:
        facts.append('You can pay online, in cash on delivery, or at the store when you pick it up.'); basis.append('payment')
    first = enq.customerName.split()[0] if enq.customerName else 'there'
    if facts:
        draft = f"Hi {first}, thanks for asking about the {product.name}. " + ' '.join(facts) + ' Let us know if you need anything else.'
        return Response({'draft': draft, 'basis': basis, 'confidence': 'high' if len(basis) >= 1 else 'low', 'note': 'Built from this product\'s details. Check it before you send.'})
    return Response({'draft': f"Hi {first}, thanks for asking about the {product.name}. ", 'basis': [], 'confidence': 'low',
                     'note': 'None of the product details answer this question, so write the answer yourself.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def seller_product_create_view(request):
    """An approved seller lists a new product. It starts with no rating or reviews (they must be earned) and no photo."""
    import uuid
    from django.utils.text import slugify
    user, company, err = _seller_or_error(request)
    if err:
        return err
    d, errors = request.data, {}
    name = str(d.get('name', '')).strip()[:200]
    category = str(d.get('category', '')).strip()[:100]
    if len(name) < 3:
        errors['name'] = 'Give the product a name (3+ characters).'
    if not category:
        errors['category'] = 'Choose a category.'
    try:
        price = float(d.get('price'))
        if price <= 0:
            raise ValueError
    except (TypeError, ValueError):
        errors['price'] = 'Enter a price above 0.'
    try:
        stock = int(d.get('stock'))
        if stock < 0 or stock > 100000:
            raise ValueError
    except (TypeError, ValueError):
        errors['stock'] = 'Enter a whole number, 0 or more.'
    if errors:
        return Response({'detail': 'Please fix the highlighted fields.', 'errors': errors}, status=http.HTTP_400_BAD_REQUEST)
    photo_url = ''
    if request.FILES.get('image'):
        photo_url, problem = save_photo(request.FILES['image'], request)
        if problem:
            return Response({'detail': problem, 'errors': {'image': problem}}, status=http.HTTP_400_BAD_REQUEST)
    pid = f'prod-{uuid.uuid4().hex[:8]}'
    product = Product.objects.create(
        id=pid, name=name, slug=f"{slugify(name)[:200]}-{pid[-4:]}", category=category, brand=str(d.get('brand', '')).strip()[:100],
        price=price, originalPrice=0, discount=0, stock=stock, description=str(d.get('description', '')).strip()[:2000],
        stockStatus='Out of Stock' if stock <= 0 else ('Low Stock' if stock <= LOW_STOCK else 'In Stock'),
        seller=company, createdAt=timezone.now().date().isoformat(), newArrival=True, images=[photo_url] if photo_url else [],
        autoRestock=str(d.get('autoRestock', '')).lower() in ('true', '1', 'yes', 'on'),
        reorderLevel=int(d.get('reorderLevel') or 5), restockQty=int(d.get('restockQty') or 20))
    StockLog.objects.create(productId=product.id, change=stock, stockAfter=stock, reason='manual', by=user.email)
    return Response({'id': product.id, 'name': product.name}, status=http.HTTP_201_CREATED)
