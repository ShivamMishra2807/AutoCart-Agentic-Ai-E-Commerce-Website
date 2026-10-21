"""
UPI "scan and pay": the customer pays the seller directly from any UPI app and the seller confirms they received it.

No payment gateway is involved, so there is nothing to sign up for and no fee:
1. At checkout the customer picks "UPI (Scan & Pay)". The order is created as "Awaiting Payment".
2. The customer scans a QR code (or taps a UPI link) that pays the seller's own UPI ID the exact order amount.
3. The customer enters the 12-digit UPI reference (UTR) from their app. The order becomes "Verifying".
4. The seller checks their bank or UPI app and confirms "Payment received" (or "Not received"). Only then is the order "Paid".

"Paid" only ever means a person who can see the money confirmed it. The same UTR can never be used on two orders.
"""

import re
import urllib.parse
import uuid

from rest_framework import status as http
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Order, Payment, Product, SellerApplication
from .views import get_user_from_token

UPI = 'UPI (Scan & Pay)'
UPI_ID = re.compile(r'^[A-Za-z0-9._-]{2,}@[A-Za-z]{2,}$')
UTR = re.compile(r'^\d{12}$')
ADMIN_ROLES = ('ADMIN', 'STAFF')


def payee_for_items(items):
    """The one seller that gets paid for these items and their UPI ID. Returns (company, upi_id, error)."""
    ids = [str(i.get('id')) for i in items or []]
    companies = {p.seller for p in Product.objects.filter(id__in=ids)}
    if len(companies) != 1 or '' in companies:
        return None, None, 'UPI payment works when the whole order is from one seller. Please pay these items separately or choose another method.'
    company = next(iter(companies))
    app = SellerApplication.objects.filter(companyName=company, status='APPROVED').first()
    if not app or not app.upiId:
        return company, None, f'{company} has not added a UPI ID yet, so UPI payment is not available. Please choose another method.'
    return company, app.upiId, None


def upi_info(order):
    company, upi_id, err = payee_for_items(order.items)
    if err:
        return None
    note = urllib.parse.quote(f'AutoCart {order.id}')
    link = f"upi://pay?pa={urllib.parse.quote(upi_id)}&pn={urllib.parse.quote(company)}&am={order.totalAmount:.2f}&cu=INR&tn={note}"
    return {'payee': company, 'upiId': upi_id, 'amount': round(order.totalAmount, 2), 'link': link, 'orderId': order.id}


def _owner_order(request, order_id):
    user = get_user_from_token(request)
    if not user:
        return None, None, Response({'detail': 'Please sign in.'}, status=http.HTTP_401_UNAUTHORIZED)
    order = Order.objects.filter(id=order_id).first()
    if not order or order.customerEmail.lower() != user.email.lower():
        return None, None, Response({'detail': 'Order not found.'}, status=http.HTTP_404_NOT_FOUND)
    if order.paymentMethod != UPI:
        return None, None, Response({'detail': 'This order is not paid by UPI.'}, status=http.HTTP_400_BAD_REQUEST)
    return user, order, None


@api_view(['GET'])
@permission_classes([AllowAny])
def order_upi_view(request, order_id):
    """The QR / link details for the customer's own UPI order."""
    user, order, err = _owner_order(request, order_id)
    if err:
        return err
    info = upi_info(order)
    if not info:
        return Response({'detail': 'UPI details are not available for this order.'}, status=http.HTTP_409_CONFLICT)
    return Response({**info, 'paymentStatus': order.paymentStatus})


@api_view(['POST'])
@permission_classes([AllowAny])
def order_upi_reference_view(request, order_id):
    """The customer says they paid and gives the UPI reference (UTR) shown in their app."""
    user, order, err = _owner_order(request, order_id)
    if err:
        return err
    if order.paymentStatus not in ('Awaiting Payment', 'Failed') or order.status == 'Cancelled':
        return Response({'detail': f"This order is '{order.paymentStatus}', so a payment reference cannot be added now."}, status=http.HTTP_400_BAD_REQUEST)
    utr = re.sub(r'\s', '', str(request.data.get('utr') or ''))
    if not UTR.match(utr):
        return Response({'detail': 'The UPI reference is 12 digits. You can find it in your UPI app under the payment details.', 'errors': {'utr': 'Enter 12 digits'}}, status=http.HTTP_400_BAD_REQUEST)
    if Payment.objects.filter(provider='upi', providerPaymentId=utr).exclude(status='FAILED').exclude(orderId=order.id).exists():
        return Response({'detail': 'That reference was already used for another order. Check the number in your UPI app.', 'errors': {'utr': 'Already used'}}, status=http.HTTP_409_CONFLICT)
    Payment.objects.update_or_create(provider='upi', orderId=order.id, status__in=['CREATED', 'VERIFYING', 'FAILED'],
                                     defaults={'id': f'pay-{uuid.uuid4().hex[:10]}', 'providerOrderId': order.id, 'providerPaymentId': utr, 'amount': order.totalAmount, 'status': 'VERIFYING'})
    order.paymentStatus = 'Verifying'
    order.save(update_fields=['paymentStatus'])
    return Response({'orderId': order.id, 'paymentStatus': order.paymentStatus, 'message': 'Thank you. The seller will check their account and confirm your payment.'})


def _may_confirm(user, order):
    if user.role in ADMIN_ROLES:
        return True
    if user.role != 'SELLER':
        return False
    app = SellerApplication.objects.filter(ownerUserId=user.id, status='APPROVED').first()
    if not app:
        return False
    mine = set(Product.objects.filter(seller=app.companyName).values_list('id', flat=True))
    return all(str(i.get('id')) in mine for i in (order.items or []))


@api_view(['POST'])
@permission_classes([AllowAny])
def payment_confirm_view(request, order_id):
    """The seller (or an admin) confirms the money arrived, or that it did not."""
    user = get_user_from_token(request)
    if not user:
        return Response({'detail': 'Please sign in.'}, status=http.HTTP_401_UNAUTHORIZED)
    order = Order.objects.filter(id=order_id).first()
    if not order or order.paymentMethod != UPI:
        return Response({'detail': 'Order not found.'}, status=http.HTTP_404_NOT_FOUND)
    if not _may_confirm(user, order):
        return Response({'detail': 'Only the seller who is being paid, or an admin, can confirm this payment.'}, status=http.HTTP_403_FORBIDDEN)
    if order.paymentStatus != 'Verifying':
        return Response({'detail': f"This payment is '{order.paymentStatus}'. There is nothing to confirm."}, status=http.HTTP_400_BAD_REQUEST)
    action = str(request.data.get('action') or '')
    if action not in ('received', 'not_received'):
        return Response({'detail': "Use 'received' or 'not_received'."}, status=http.HTTP_400_BAD_REQUEST)
    ok = action == 'received'
    Payment.objects.filter(orderId=order.id, provider='upi', status='VERIFYING').update(status='PAID' if ok else 'FAILED')
    order.paymentStatus = 'Paid' if ok else 'Failed'
    if ok:
        order.status = 'Confirmed'
        order.timeline = [({**t, 'status': 'Payment received', 'completed': True} if t.get('status') == 'Waiting for payment' else t) for t in (order.timeline or [])]
    order.save(update_fields=['paymentStatus', 'status', 'timeline'])
    return Response({'orderId': order.id, 'paymentStatus': order.paymentStatus, 'status': order.status})


@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def seller_payout_settings_view(request):
    """A seller's own UPI ID: where customers' UPI payments go."""
    user = get_user_from_token(request)
    if not user or user.role != 'SELLER':
        return Response({'detail': 'This is for sellers.'}, status=http.HTTP_403_FORBIDDEN if user else http.HTTP_401_UNAUTHORIZED)
    app = SellerApplication.objects.filter(ownerUserId=user.id, status='APPROVED').first()
    if not app:
        return Response({'detail': 'Your seller account is not active yet.'}, status=http.HTTP_403_FORBIDDEN)
    if request.method == 'PUT':
        upi = str(request.data.get('upiId') or '').strip()
        if upi and not UPI_ID.match(upi):
            return Response({'detail': 'A UPI ID looks like name@bank, for example shop@okaxis.', 'errors': {'upiId': 'Not a valid UPI ID'}}, status=http.HTTP_400_BAD_REQUEST)
        app.upiId = upi
        app.save(update_fields=['upiId'])
    return Response({'upiId': app.upiId})


@api_view(['GET'])
@permission_classes([AllowAny])
def payments_admin_view(request):
    """Admin overview of how people pay, and UPI payments waiting for a seller to confirm."""
    user = get_user_from_token(request)
    if not user or user.role not in ADMIN_ROLES:
        return Response({'detail': 'Only an administrator can see this.'}, status=http.HTTP_403_FORBIDDEN)
    methods = {}
    for o in Order.objects.exclude(status='Cancelled'):
        m = methods.setdefault(o.paymentMethod, {'method': o.paymentMethod, 'orders': 0, 'amount': 0.0, 'paid': 0})
        m['orders'] += 1
        m['amount'] += o.totalAmount
        m['paid'] += 1 if o.paymentStatus == 'Paid' else 0
    waiting = []
    for pay in Payment.objects.filter(provider='upi', status='VERIFYING').order_by('createdAt')[:30]:
        o = Order.objects.filter(id=pay.orderId).first()
        if o:
            company = payee_for_items(o.items)[0]
            waiting.append({'orderId': o.id, 'customer': o.customerName, 'amount': o.totalAmount, 'utr': pay.providerPaymentId, 'seller': company, 'since': pay.createdAt})
    return Response({'methods': [{**m, 'amount': round(m['amount'])} for m in methods.values()], 'waiting': waiting})


@api_view(['POST'])
@permission_classes([AllowAny])
def upi_check_view(request):
    """Checkout asks this before offering "Pay now with UPI": it works only when the whole cart is from one seller who has a UPI ID."""
    items = [{'id': str(i.get('id'))} for i in (request.data.get('items') or []) if isinstance(i, dict) and i.get('id')]
    if not items:
        return Response({'available': False, 'reason': 'Your cart is empty.'})
    company, upi_id, problem = payee_for_items(items)
    return Response({'available': problem is None, 'payee': company if problem is None else None, 'reason': problem or ''})
