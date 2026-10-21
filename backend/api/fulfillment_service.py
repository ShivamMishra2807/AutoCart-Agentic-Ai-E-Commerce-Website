"""
AutoCart Concurrency-Safe Order Reservation & Delivery Fulfillment Service.
Handles atomic inventory reservations, checkout quotes, delivery provider abstraction,
and order tracking status reconciliation.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from django.db import transaction
from .models import Store, StoreInventory, Product, Order, OrderFulfillment, InventoryReservation
from .location_service import haversine_distance_km

class FulfillmentService:
    """
    Manages stock reservations, delivery estimation, and fulfillment lifecycle.
    """

    RESERVATION_EXPIRY_MINUTES = 15

    @classmethod
    def create_stock_reservation(
        cls,
        store_id: str,
        product_id: str,
        quantity: int,
        user_email: str
    ) -> Dict[str, Any]:
        """
        Atomically checks and reserves store inventory for 15 minutes using database row locking.
        Prevents overselling when multiple customers attempt to purchase the last available item.
        """
        if quantity <= 0:
            return {'success': False, 'error': 'Requested quantity must be at least 1'}

        with transaction.atomic():
            inv = StoreInventory.objects.select_for_update().filter(
                store_id=store_id,
                product_id=product_id
            ).first()

            if not inv:
                return {'success': False, 'error': f"Product {product_id} is not stocked at store {store_id}."}

            if inv.availableQuantity < quantity:
                return {
                    'success': False,
                    'error': f"Insufficient stock. Only {inv.availableQuantity} unit(s) available at {inv.store.name}."
                }

            # Decrement available quantity and increment reserved quantity atomically
            inv.availableQuantity -= quantity
            inv.reservedQuantity += quantity
            inv.isAvailable = (inv.availableQuantity > 0)
            inv.save()

            # Create reservation record
            token = f"res_{uuid.uuid4().hex[:16]}"
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=cls.RESERVATION_EXPIRY_MINUTES)

            res = InventoryReservation.objects.create(
                id=f"res-{uuid.uuid4().hex[:8]}",
                store=inv.store,
                product=inv.product,
                quantity=quantity,
                reservationToken=token,
                userEmail=user_email,
                status='Active',
                expiresAt=expires_at
            )

            return {
                'success': True,
                'reservationToken': token,
                'reservationId': res.id,
                'storeId': store_id,
                'storeName': inv.store.name,
                'productId': product_id,
                'productName': inv.product.name,
                'quantity': quantity,
                'expiresAt': expires_at.isoformat(),
                'expiresInMinutes': cls.RESERVATION_EXPIRY_MINUTES
            }

    @classmethod
    def confirm_stock_reservation(cls, reservation_token: str) -> bool:
        """
        Marks reservation as confirmed upon successful order payment.
        Converts reserved stock to permanently deducted inventory.
        """
        with transaction.atomic():
            res = InventoryReservation.objects.select_for_update().filter(
                reservationToken=reservation_token,
                status='Active'
            ).first()

            if not res:
                return False

            inv = StoreInventory.objects.select_for_update().filter(
                store=res.store,
                product=res.product
            ).first()

            if inv:
                inv.reservedQuantity = max(0, inv.reservedQuantity - res.quantity)
                inv.save()

            res.status = 'Confirmed'
            res.save()
            return True

    @classmethod
    def release_stock_reservation(cls, reservation_token: str, reason: str = 'Cancelled') -> bool:
        """
        Releases reserved stock back to available quantity if checkout is cancelled or expires.
        """
        with transaction.atomic():
            res = InventoryReservation.objects.select_for_update().filter(
                reservationToken=reservation_token,
                status='Active'
            ).first()

            if not res:
                return False

            inv = StoreInventory.objects.select_for_update().filter(
                store=res.store,
                product=res.product
            ).first()

            if inv:
                inv.availableQuantity += res.quantity
                inv.reservedQuantity = max(0, inv.reservedQuantity - res.quantity)
                inv.isAvailable = True
                inv.save()

            res.status = 'Released'
            res.save()
            return True

    @classmethod
    def generate_checkout_quote(
        cls,
        product_id: str,
        quantity: int,
        store_id: Optional[str] = None,
        customer_lat: float = 19.0760,
        customer_lng: float = 72.8777
    ) -> Dict[str, Any]:
        """
        Generates authoritative item subtotal, distance delivery charge, tax, and estimated delivery ETA.
        Validates store hyperlocal serviceability radius against customer location.
        """
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return {'error': f"Product {product_id} not found"}

        store = None
        dist_km = 4.2
        delivery_minutes = 35
        is_serviceable = True
        warning = None

        if store_id:
            store = Store.objects.filter(id=store_id).first()
            if store:
                dist_km = haversine_distance_km(customer_lat, customer_lng, store.latitude, store.longitude)
                delivery_minutes = max(25, int(dist_km * 3.2) + 15)
                effective_radius = store.serviceCoverageRadiusKm
                if dist_km > effective_radius:
                    is_serviceable = False
                    warning = (
                        f"Selected store {store.name} is {dist_km:.1f} km away, which exceeds its "
                        f"delivery coverage radius of {effective_radius:.1f} km. Please choose a closer store or switch to standard delivery."
                    )

        unit_price = float(product.price)
        subtotal = round(unit_price * quantity, 2)
        tax = round(subtotal * 0.18, 2)  # 18% standard GST
        
        # Delivery fee: Free for orders > ₹499 or within 3km of store
        delivery_fee = 0.0 if (subtotal >= 499 or dist_km <= 3.0) else round(35.0 + max(0, dist_km - 3.0) * 8.0, 2)
        total_amount = round(subtotal + tax + delivery_fee, 2)

        return {
            'productId': product.id,
            'productName': product.name,
            'unitPrice': unit_price,
            'quantity': quantity,
            'subtotal': subtotal,
            'tax': tax,
            'deliveryFee': delivery_fee,
            'totalAmount': total_amount,
            'storeId': store.id if store else None,
            'storeName': store.name if store else 'AutoCart Central Warehouse',
            'distanceKm': dist_km,
            'estimatedMinutes': delivery_minutes,
            'isServiceable': is_serviceable,
            'serviceCoverageRadiusKm': store.serviceCoverageRadiusKm if store else 25.0,
            'warning': warning,
            'currency': 'INR',
            'currencySymbol': '₹'
        }

    @classmethod
    def initiate_fulfillment(
        cls,
        order: Order,
        store: Optional[Store] = None,
        fulfillment_type: str = 'Store Delivery'
    ) -> OrderFulfillment:
        """
        Initializes OrderFulfillment with tracking number and multi-stage status timeline.
        Clearly labels development mode / simulation adapter.
        """
        now = datetime.now(timezone.utc)
        tracking_num = f"TRK-HYP-{uuid.uuid4().hex[:8].upper()}"

        timeline = [
            {'status': 'Order Placed & Payment Confirmed', 'time': now.strftime('%I:%M %p'), 'completed': True},
            {'status': 'Allocated to Store / Partner', 'time': now.strftime('%I:%M %p'), 'completed': True},
            {'status': 'Packing & Quality Verification', 'time': (now + timedelta(minutes=10)).strftime('%I:%M %p'), 'completed': False},
            {'status': 'Out for Hyperlocal Delivery', 'time': (now + timedelta(minutes=25)).strftime('%I:%M %p'), 'completed': False},
            {'status': 'Delivered to Customer Doorstep', 'time': (now + timedelta(minutes=45)).strftime('%I:%M %p'), 'completed': False},
        ]

        dest_addr = order.shippingAddress or {}
        fulfillment, _ = OrderFulfillment.objects.update_or_create(
            order=order,
            defaults={
                'id': f"ful-{order.id}",
                'store': store,
                'fulfillmentType': fulfillment_type,
                'deliveryPartner': 'AutoCart Hyperlocal Express (Dev Mode Adapter)',
                'trackingNumber': tracking_num,
                'currentStatus': 'Order Allocated',
                'distanceKm': 3.8 if store else 8.5,
                'estimatedDeliveryMinutes': 35 if store else 60,
                'deliveryAddress': dest_addr,
                'timeline': timeline
            }
        )
        return fulfillment
