"""
Orders and payments.

Rules enforced on the server (the browser is never trusted for money):
- Prices, coupon discount, delivery fee and the total are worked out here from the database.
- Stock is checked and reduced inside one transaction, so two people cannot buy the last item.
- The order belongs to the signed-in user. Nobody else can see, track, return or cancel it.
- "Paid" only ever means a payment was verified. Cash on Delivery and Pay at Store stay "Pending".

Payment methods (no payment gateway is used): Cash on Delivery, UPI or Card on Delivery, Pay at Store, and UPI (Scan & Pay),
where the customer pays the seller's own UPI ID and the seller confirms receipt (see upi_payments.py).
"""

import datetime
import random

from django.db import transaction
from rest_framework import status as http
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .fulfillment_service import FulfillmentService
from .models import Coupon, InventoryReservation, Order, OrderFulfillment, Product, Store, User
from .serializers import OrderFulfillmentSerializer, OrderSerializer
from .views import get_user_from_token

from .stock_rules import log_sale
from .upi_payments import UPI, payee_for_items, upi_info

ADMIN_ROLES = ('ADMIN', 'STAFF')
COD, POD, STORE = 'Cash on Delivery', 'UPI or Card on Delivery', 'Pay at Store'
PAYMENT_METHODS = (COD, POD, STORE, UPI)
MAX_QTY = 20
CANCELLABLE = ('Pending', 'Confirmed', 'Processing')


# ---------------------------------------------------------------- helpers --

def _unauth():
    return Response({'detail': 'Please sign in to continue.'}, status=http.HTTP_401_UNAUTHORIZED)


def _order_for(request, order_id):
    """(order, user, error). Admins see any order; everyone else only their own. A stranger gets 404, not 403."""
    user = get_user_from_token(request)
    if not user:
        return None, None, _unauth()
    order = Order.objects.filter(id=order_id).first()
    if not order or (user.role not in ADMIN_ROLES and (order.customerEmail or '').lower() != user.email.lower()):
        return None, user, Response({'detail': 'Order not found.'}, status=http.HTTP_404_NOT_FOUND)
    return order, user, None


def coupon_discount(coupon: Coupon, subtotal: float) -> float:
    if coupon.discountType == 'Percentage':
        raw = subtotal * coupon.discountValue / 100.0
    else:
        raw = coupon.discountValue
    return round(min(raw, coupon.maxDiscount) if coupon.maxDiscount else raw)


def stock_label(stock: int) -> str:
    return 'Out of Stock' if stock <= 0 else ('Low Stock' if stock <= 10 else 'In Stock')


def delivery_fee(subtotal: float, coupon_code: str) -> float:
    if subtotal <= 0:
        return 0.0
    return 0.0 if subtotal > 499 or coupon_code == 'FREESHIP' else 40.0


# ------------------------------------------------------------ create order --

def create_order(request):
    user = get_user_from_token(request)
    if not user:
        return _unauth()
    if user.role != 'CUSTOMER':
        return Response({'detail': 'Only customer accounts can place orders. Sellers and admins cannot buy.'}, status=http.HTTP_403_FORBIDDEN)
    data = request.data
    method = str(data.get('paymentMethod') or COD)
    if method not in PAYMENT_METHODS:
        return Response({'detail': f"Choose one of: {', '.join(PAYMENT_METHODS)}."}, status=http.HTTP_400_BAD_REQUEST)

    wanted = {}
    for row in data.get('items') or []:
        try:
            qty = int(row.get('quantity') or 1)
        except (TypeError, ValueError):
            qty = 0
        if not row.get('id') or not 1 <= qty <= MAX_QTY:
            return Response({'detail': f'Each item needs a valid quantity (1 to {MAX_QTY}).'}, status=http.HTTP_400_BAD_REQUEST)
        wanted[str(row['id'])] = wanted.get(str(row['id']), 0) + qty
    if not wanted:
        return Response({'detail': 'Your cart is empty.'}, status=http.HTTP_400_BAD_REQUEST)

    shipping = dict(data.get('shippingAddress') or {})
    if method == UPI:  # the money goes straight to the seller, so there must be exactly one seller with a UPI ID
        _company, _upi, problem = payee_for_items([{'id': i} for i in wanted])
        if problem:
            return Response({'detail': problem}, status=http.HTTP_400_BAD_REQUEST)
    store = Store.objects.filter(id=data.get('storeId') or shipping.get('storeId')).first()
    if store:
        shipping['storeId'], shipping['storeName'] = store.id, store.name
    if method == STORE and not store:
        return Response({'detail': 'Choose the store where you will pay and pick up.'}, status=http.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        products = {p.id: p for p in Product.objects.select_for_update().filter(id__in=wanted)}
        missing = [pid for pid in wanted if pid not in products]
        if missing:
            return Response({'detail': 'Some items are no longer available. Please review your cart.'}, status=http.HTTP_400_BAD_REQUEST)
        lines, subtotal = [], 0.0
        for pid, qty in wanted.items():
            p = products[pid]
            if p.stock < qty:
                msg = f'{p.name} is out of stock.' if p.stock <= 0 else f'Only {p.stock} of {p.name} left. Please lower the quantity.'
                return Response({'detail': msg}, status=http.HTTP_409_CONFLICT)
            lines.append({'id': p.id, 'name': p.name, 'brand': p.brand, 'category': p.category, 'price': p.price, 'quantity': qty,
                          'image': (p.images or [''])[0], 'images': p.images or []})
            subtotal += p.price * qty

        code = str(data.get('couponCode') or '').strip().upper()
        discount = 0.0
        if code:
            coupon = Coupon.objects.filter(code__iexact=code, status='Active').first()
            if not coupon or subtotal < coupon.minOrderAmount:
                return Response({'detail': 'That coupon is not valid for this order.'}, status=http.HTTP_400_BAD_REQUEST)
            discount = float(coupon_discount(coupon, subtotal))
        fee = delivery_fee(subtotal, code)
        total = max(0.0, subtotal - discount + fee)

        for pid, qty in wanted.items():
            p = products[pid]
            p.stock -= qty
            p.stockStatus = stock_label(p.stock)
            p.save(update_fields=['stock', 'stockStatus'])
            log_sale(p, qty)

        now = datetime.datetime.now()
        order_id = f"ORD-{now.year}-{random.randint(1000, 9999)}"
        while Order.objects.filter(id=order_id).exists():
            order_id = f"ORD-{now.year}-{random.randint(1000, 9999)}"
        timeline = [
            {'status': 'Order Placed', 'time': now.strftime('%I:%M %p'), 'completed': True},
            {'status': 'Confirmed' if method != UPI else 'Waiting for payment', 'time': now.strftime('%I:%M %p'), 'completed': method != UPI},
            {'status': 'Processing', 'time': '', 'completed': False},
            {'status': 'Out for Delivery' if method != STORE else 'Ready for pickup', 'time': '', 'completed': False},
            {'status': 'Delivered' if method != STORE else 'Picked up', 'time': '', 'completed': False},
        ]
        order = Order.objects.create(
            id=order_id, customerName=shipping.get('fullName') or user.name, customerEmail=user.email,
            customerPhone=shipping.get('phone') or user.phone, date=now.strftime('%Y-%m-%d'), totalAmount=total, subtotal=subtotal,
            tax=0.0, shippingFee=fee, discountAmount=discount, paymentMethod=method,
            paymentStatus='Awaiting Payment' if method == UPI else 'Pending',
            status='Pending' if method == UPI else 'Confirmed', shippingAddress=shipping, items=lines, timeline=timeline,
        )
        FulfillmentService.initiate_fulfillment(order, store=store, fulfillment_type='Store Pickup' if method == STORE else 'Store Delivery')
        user.ordersCount += 1
        user.totalSpent += total
        user.save(update_fields=['ordersCount', 'totalSpent'])

    body = OrderSerializer(order).data
    body['paymentRequired'] = method == UPI
    body['upi'] = upi_info(order) if method == UPI else None
    return Response(body, status=http.HTTP_201_CREATED)


# ------------------------------------------- tracking, return, cancellation --

@api_view(['GET'])
@permission_classes([AllowAny])
def order_tracking_view(request, order_id):
    order, _, err = _order_for(request, order_id)
    if err:
        return err
    fulfillment = OrderFulfillment.objects.filter(order=order).first() or FulfillmentService.initiate_fulfillment(order)
    data = OrderFulfillmentSerializer(fulfillment).data
    if fulfillment.store:
        data['storeLocation'] = {'name': fulfillment.store.name, 'address': fulfillment.store.address, 'latitude': fulfillment.store.latitude,
                                 'longitude': fulfillment.store.longitude, 'phone': fulfillment.store.phone}
    from .seller_orders import drop_point, order_pickup
    data['orderStatus'] = order.status
    data['customerLocation'] = drop_point(order)
    data['pickup'] = order_pickup(order)
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def order_return_view(request, order_id):
    order, _, err = _order_for(request, order_id)
    if err:
        return err
    if order.status not in ('Delivered', 'Completed'):
        return Response({'success': False, 'detail': f"Order {order.id} is '{order.status}'. Returns are only for delivered orders."},
                        status=http.HTTP_400_BAD_REQUEST)
    order.status = 'Return Requested'
    order.save(update_fields=['status'])
    return Response({'success': True, 'orderId': order.id, 'status': order.status,
                     'message': 'Return request accepted. Our team will contact you about pickup.',
                     'returnPolicy': '7-day window. Refunds are processed after inspection.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def order_cancel_view(request, order_id):
    order, _, err = _order_for(request, order_id)
    if err:
        return err
    if order.status not in CANCELLABLE:
        return Response({'success': False, 'detail': f"Order {order.id} is '{order.status}' and can't be cancelled now."}, status=http.HTTP_400_BAD_REQUEST)
    with transaction.atomic():
        for line in order.items or []:  # put the stock back
            p = Product.objects.select_for_update().filter(id=line.get('id')).first()
            if p:
                p.stock += int(line.get('quantity') or 0)
                p.stockStatus = stock_label(p.stock)
                p.save(update_fields=['stock', 'stockStatus'])
        was_paid = order.paymentStatus == 'Paid'
        order.status = 'Cancelled'
        order.paymentStatus = 'Refund Pending' if was_paid else ('Cancelled' if order.paymentStatus in ('Awaiting Payment', 'Pending', 'Failed') else order.paymentStatus)
        order.save(update_fields=['status', 'paymentStatus'])
        for res in InventoryReservation.objects.filter(userEmail=order.customerEmail, status='Active'):
            FulfillmentService.release_stock_reservation(res.reservationToken, reason=f'Order {order.id} cancelled')
    return Response({'success': True, 'orderId': order.id, 'status': 'Cancelled',
                     'message': 'Your order is cancelled.' + (' Your payment will be refunded by our team.' if was_paid else '')})
