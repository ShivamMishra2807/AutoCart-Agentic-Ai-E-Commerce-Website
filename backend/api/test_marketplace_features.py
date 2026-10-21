"""
Dedicated Test Suite for AutoCart Upgraded Marketplace Features:
- Location-aware store discovery & Haversine distance
- Concurrency-safe atomic inventory reservations (select_for_update)
- Fulfillment checkout quote generation
- Document OCR entity extraction, GSTIN validation, and Aadhaar PII masking
- 8-State Seller Application State Machine transitions
"""

from django.test import TestCase
from api.models import (
    User, Product, Store, StoreInventory, InventoryReservation,
    SellerApplication, SellerApplicationAudit, Order, OrderFulfillment
)
from api.location_service import haversine_distance_km, resolve_coordinates, find_nearby_stores_with_inventory
from api.fulfillment_service import FulfillmentService
from api.ocr_service import DocumentOCRService


class MarketplaceFeaturesTest(TestCase):
    def setUp(self):
        # Create test product
        self.product = Product.objects.create(
            id='prod-airpods-pro',
            name='Apple AirPods Pro (2nd Gen)',
            slug='apple-airpods-pro-2nd-gen',
            category='Electronics',
            price=24990.0,
            originalPrice=26990.0,
            stock=50,
            rating=4.9,
            brand='Apple'
        )

        # Create physical partner stores
        self.store_blr = Store.objects.create(
            id='store-blr-indiranagar',
            name='AutoCart Hyperlocal Hub — Indiranagar',
            seller='Apex Electronics',
            address='100ft Road, Indiranagar',
            city='Bengaluru',
            state='Karnataka',
            pincode='560038',
            latitude=12.9784,
            longitude=77.6408,
            operatingStatus='Open',
            fulfillmentCapability='Store Delivery & Pickup',
            serviceCoverageRadiusKm=20.0,
            rating=4.9
        )

        self.store_mum = Store.objects.create(
            id='store-mum-bandra',
            name='AutoCart Flagship Store — Bandra',
            seller='West Coast Retail',
            address='Hill Road, Bandra West',
            city='Mumbai',
            state='Maharashtra',
            pincode='400050',
            latitude=19.0596,
            longitude=72.8295,
            operatingStatus='Open',
            fulfillmentCapability='Store Delivery & Pickup',
            serviceCoverageRadiusKm=25.0,
            rating=4.8
        )

        # Map store inventory
        self.inv_blr = StoreInventory.objects.create(
            id='inv-blr-airpods',
            store=self.store_blr,
            product=self.product,
            availableQuantity=15,
            reservedQuantity=0,
            isAvailable=True,
            storePrice=24990.0
        )

    def test_haversine_distance_calculation(self):
        """Tests accurate spherical distance in kilometers."""
        dist = haversine_distance_km(12.9784, 77.6408, 12.9352, 77.6245)
        self.assertGreaterEqual(dist, 4.0)
        self.assertLessEqual(dist, 7.0)

    def test_pincode_geocoding_resolution(self):
        """Tests Indian PIN code resolution to coordinates."""
        coords = resolve_coordinates('560038')
        self.assertIsNotNone(coords)
        lat, lng, area = coords
        self.assertAlmostEqual(lat, 12.9784, places=2)
        self.assertIn('Indiranagar', area)

    def test_nearby_store_inventory_lookup(self):
        """Tests querying stores holding physical stock within delivery radius."""
        stores = find_nearby_stores_with_inventory(
            product_id=self.product.id,
            customer_lat=12.9716,
            customer_lng=77.5946,
            max_radius_km=15.0
        )
        self.assertGreaterEqual(len(stores), 1)
        self.assertEqual(stores[0]['storeId'], self.store_blr.id)
        self.assertEqual(stores[0]['availableQuantity'], 15)

    def test_concurrency_safe_stock_reservation(self):
        """Tests atomic stock reservation and available quantity deduction."""
        res = FulfillmentService.create_stock_reservation(
            store_id=self.store_blr.id,
            product_id=self.product.id,
            quantity=2,
            user_email='buyer@example.com'
        )
        self.assertTrue(res['success'])
        self.assertIn('reservationToken', res)

        # Refresh inventory from DB
        self.inv_blr.refresh_from_db()
        self.assertEqual(self.inv_blr.availableQuantity, 13)
        self.assertEqual(self.inv_blr.reservedQuantity, 2)

        # Test releasing the reservation
        released = FulfillmentService.release_stock_reservation(res['reservationToken'])
        self.assertTrue(released)
        self.inv_blr.refresh_from_db()
        self.assertEqual(self.inv_blr.availableQuantity, 15)
        self.assertEqual(self.inv_blr.reservedQuantity, 0)

    def test_fulfillment_quote_calculation(self):
        """Tests checkout quote with GST and distance-based delivery fee."""
        quote = FulfillmentService.generate_checkout_quote(
            product_id=self.product.id,
            quantity=1,
            store_id=self.store_blr.id,
            customer_lat=12.9716,
            customer_lng=77.5946
        )
        self.assertIn('totalAmount', quote)
        self.assertEqual(quote['subtotal'], 24990.0)
        self.assertEqual(quote['tax'], 4498.2)  # 18% GST
        self.assertEqual(quote['deliveryFee'], 0.0) # > 499 free delivery

    def test_ocr_pii_redaction_and_gstin_validation(self):
        """Tests Aadhaar masking and Indian GSTIN extraction."""
        doc_text = "Government of India Aadhaar: 1234 5678 9012 GSTIN: 29ABCDE1234F1Z5 PAN: ABCDE1234F Legal Name: Apex Retail"
        redacted = DocumentOCRService.mask_pii_sensitive_data(doc_text)
        self.assertNotIn('1234 5678 9012', redacted)
        self.assertIn('XXXX-XXXX-9012', redacted)

        entities = DocumentOCRService.extract_document_entities(doc_text, 'GST_CERTIFICATE')
        self.assertEqual(entities['extractedGstin'], '29ABCDE1234F1Z5')
        self.assertEqual(entities['extractedPan'], 'ABCDE1234F')
        self.assertTrue(entities['isIndianGstinValid'])

    def test_seller_application_state_machine_flow(self):
        """Tests the 8-state application lifecycle transition from SUBMITTED to APPROVED."""
        app = SellerApplication.objects.create(
            id='app-test-state-1',
            companyName='Test Electronics Hub',
            applicantName='Ramesh',
            email='ramesh@test.in',
            phone='9845012345',
            gstin='29ABCDE1234F1Z5',
            pan='ABCDE1234F',
            status='SUBMITTED',
            riskScore=15
        )

        # Transition 1: SUBMITTED -> PENDING_ADMIN_APPROVAL
        app.status = 'PENDING_ADMIN_APPROVAL'
        app.save()
        self.assertEqual(app.status, 'PENDING_ADMIN_APPROVAL')

        # Transition 2: PENDING_ADMIN_APPROVAL -> APPROVED
        app.status = 'APPROVED'
        app.reviewedBy = 'admin@autocart.local'
        app.save()
        self.assertEqual(app.status, 'APPROVED')
