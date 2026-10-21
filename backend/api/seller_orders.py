"""
Seller order handling: one click to confirm an order is packed, and the pickup-to-doorstep route for it.

A seller only ever acts on orders that contain their own products. The pickup point is the seller's own store location
(from their approved application, or their store row), and the drop point is the location the customer shared at checkout.
"""

import math

from django.utils import timezone
from rest_framework import status as http
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Order, OrderFulfillment, Product, SellerApplication, Store
from .role_views import _seller_or_error

PACKABLE = ('Confirmed', 'Processing', 'Pending', 'Order Placed')


def _km(a, b):
    """Straight-line distance in km between two (lat, lng) points."""
    r = 6371.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def _num(v):
    try:
        f = float(v)
        return f if f else None
    except (TypeError, ValueError):
        return None


def pickup_for_company(company):
    """The pickup point of a seller found by company name (used when a customer looks at their own order)."""
    app = SellerApplication.objects.filter(companyName=company, status='APPROVED').first()
    if app and _num(app.storeLatitude) and _num(app.storeLongitude):
        return {'name': app.storeName or company, 'address': app.address or '', 'lat': app.storeLatitude, 'lng': app.storeLongitude}
    store = Store.objects.filter(seller=company).first()
    if store and store.latitude:
        return {'name': store.name, 'address': store.address, 'lat': store.latitude, 'lng': store.longitude}
    return None


def order_pickup(order):
    """Where the first seller in this order packs from."""
    for i in order.items or []:
        p = Product.objects.filter(id=str(i.get('id'))).first()
        if p and p.seller:
            found = pickup_for_company(p.seller)
            if found:
                return found
    return None


def pickup_point(user, company):
    """Where this seller packs from: their application's store pin, else a store row carrying their name."""
    app = SellerApplication.objects.filter(ownerUserId=user.id, status='APPROVED').first()
    if app and _num(app.storeLatitude) and _num(app.storeLongitude):
        return {'name': app.storeName or company, 'address': app.address or '', 'lat': app.storeLatitude, 'lng': app.storeLongitude}
    store = Store.objects.filter(seller=company).first()
    if store and store.latitude:
        return {'name': store.name, 'address': store.address, 'lat': store.latitude, 'lng': store.longitude}
    return None


def drop_point(order):
    a = order.shippingAddress or {}
    lat, lng = _num(a.get('latitude')), _num(a.get('longitude'))
    text = ', '.join(x for x in (a.get('addressLine'), a.get('city'), a.get('pinCode') or a.get('pincode')) if x)
    return {'name': order.customerName.split()[0] if order.customerName else 'Customer', 'address': text, 'lat': lat, 'lng': lng} if lat and lng else None


def _my_order(company, order_id):
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return None
    mine = set(Product.objects.filter(seller=company).values_list('id', flat=True))
    return order if any(str(i.get('id')) in mine for i in (order.items or [])) else None


@api_view(['POST'])
@permission_classes([AllowAny])
def seller_pack_order_view(request, order_id):
    """One click: the seller confirms the order is packed and ready. The customer's tracking updates."""
    user, company, err = _seller_or_error(request)
    if err:
        return err
    order = _my_order(company, order_id)
    if not order:
        return Response({'detail': 'Order not found.'}, status=http.HTTP_404_NOT_FOUND)
    if order.paymentMethod == 'UPI (Scan & Pay)' and order.paymentStatus != 'Paid':
        return Response({'detail': 'Confirm that the UPI payment arrived before packing this order.'}, status=http.HTTP_400_BAD_REQUEST)
    if order.status not in PACKABLE:
        return Response({'detail': f"This order is '{order.status}', so it cannot be marked packed now."}, status=http.HTTP_400_BAD_REQUEST)
    order.status = 'Packed'
    order.timeline = list(order.timeline or []) + [{'status': f'Packed by {company}', 'time': timezone.now().strftime('%d %b %I:%M %p'), 'completed': True}]
    order.save(update_fields=['status', 'timeline'])
    ful = OrderFulfillment.objects.filter(order=order).first()
    if ful:
        ful.currentStatus = 'Packed, ready for pickup'
        ful.timeline = [{**step, 'completed': True} if 'Packing' in str(step.get('status')) or step.get('completed') else step for step in (ful.timeline or [])]
        ful.save(update_fields=['currentStatus', 'timeline'])
    return Response({'id': order.id, 'status': order.status})


@api_view(['GET'])
@permission_classes([AllowAny])
def seller_order_route_view(request, order_id):
    """Pickup and drop points with the straight-line distance. The browser asks a free routing service for the road route."""
    user, company, err = _seller_or_error(request)
    if err:
        return err
    order = _my_order(company, order_id)
    if not order:
        return Response({'detail': 'Order not found.'}, status=http.HTTP_404_NOT_FOUND)
    pickup, drop = pickup_point(user, company), drop_point(order)
    km = round(_km((pickup['lat'], pickup['lng']), (drop['lat'], drop['lng'])), 1) if pickup and drop else None
    note = '' if pickup and drop else ('Add your store location in your seller profile.' if not pickup else 'The customer did not share a map location for this order.')
    return Response({'orderId': order.id, 'status': order.status, 'pickup': pickup, 'drop': drop, 'straightLineKm': km, 'note': note})
