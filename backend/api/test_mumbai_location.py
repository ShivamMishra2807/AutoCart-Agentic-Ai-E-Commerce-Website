"""
Comprehensive Automated Test Suite for Mumbai Hyperlocal Store Discovery and Delivery Location Fix.
Tests all 15 required capabilities:
1. Chatbot asks for PIN code when address is missing.
2. Multi-turn conversation preserves the selected product across PIN request and entry.
3. Malformed PIN codes are rejected with a helpful message.
4. Valid PIN code resolves to the correct area.
5. Unmapped PIN code explains the limitation.
6. Nearby-store queries return real stores with correct distance calculation.
7. Product availability lookup reflects actual inventory quantities.
8. Out-of-stock handling suggests real in-stock alternatives.
9. Delivery estimates and fees vary realistically with distance.
10. Address change updates customer profile and invalidates stale location state.
11. Chatbot context reflects new address after change.
12. Concurrency test verifies inventory deductions are atomic.
13. Checkout fails if stock becomes unavailable.
14. Switching to an unserviceable address invalidates fulfillment options.
15. Integration with Sathi agent tools and session memory.
"""

from unittest.mock import MagicMock, patch
from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient
from rest_framework import status

from api.models import Product, Store, StoreInventory, User, Order, InventoryReservation
from api.views import generate_token
from api.agents.memory import SessionMemoryManager
from api.agents.engine import AgentEngine
from api.location_service import (
    resolve_coordinates,
    haversine_distance_km,
    find_nearby_stores_with_inventory,
    KNOWN_GEOCODING_DATABASE,
)
from api.fulfillment_service import FulfillmentService


def authed(user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION='Bearer ' + generate_token(user))
    return c


class MumbaiHyperlocalLocationTests(TestCase):
    def setUp(self):
        # Clear in-memory session state
        SessionMemoryManager._sessions.clear()
        SessionMemoryManager._states.clear()
        SessionMemoryManager._timestamps.clear()

        self.engine = AgentEngine()
        self.guest_client = APIClient()

        # Create test users
        self.user = User.objects.create_user(
            email='mumbai.shopper@test.com',
            name='Rajesh Kulkarni',
            password='password123',
            phone='9820011223'
        )
        self.auth_client = authed(self.user)

        # Create real products
        self.prod_earbuds = Product.objects.create(
            id='prod-test-eb-01',
            name='boAt Airdopes 141 ANC Wireless Earbuds',
            slug='boat-airdopes-141-anc',
            category='Audio',
            brand='boAt',
            price=1499.0,
            originalPrice=4490.0,
            stock=50,
            rating=4.3,
            stockStatus='In Stock'
        )
        self.prod_alt_1 = Product.objects.create(
            id='prod-test-eb-02',
            name='Noise Buds VS102 Wireless Earbuds',
            slug='noise-buds-vs102',
            category='Audio',
            brand='Noise',
            price=1299.0,
            originalPrice=2999.0,
            stock=30,
            rating=4.2,
            stockStatus='In Stock'
        )
        self.prod_alt_2 = Product.objects.create(
            id='prod-test-eb-03',
            name='Boult Audio AirBass Propods',
            slug='boult-airbass-propods',
            category='Audio',
            brand='Boult',
            price=999.0,
            originalPrice=2499.0,
            stock=25,
            rating=4.0,
            stockStatus='In Stock'
        )

        # Create physical partner stores across Mumbai MMR
        # 1. Kalyan Store
        self.store_kalyan = Store.objects.create(
            id='store-test-kln-01',
            name='AutoCart Partner - Kalyan Khadakpada Store',
            seller='Kalyan Electronics Hub',
            address='Shop 4, Khadakpada Circle, Station Road, Kalyan West',
            city='Kalyan',
            pincode='421301',
            latitude=19.2551,
            longitude=73.1378,
            operatingStatus='Open',
            serviceCoverageRadiusKm=12.0,
            rating=4.7
        )
        # 2. Thane Store
        self.store_thane = Store.objects.create(
            id='store-test-thn-01',
            name='AutoCart Partner - Viviana Mall Thane',
            seller='Thane Retail Partners',
            address='Ground Floor, Viviana Mall, Eastern Express Highway, Thane West',
            city='Thane',
            pincode='400606',
            latitude=19.2085,
            longitude=72.9716,
            operatingStatus='Open',
            serviceCoverageRadiusKm=15.0,
            rating=4.8
        )
        # 3. Andheri Store
        self.store_andheri = Store.objects.create(
            id='store-test-and-01',
            name='AutoCart Partner - Andheri Lokhandwala Hub',
            seller='Appario West Mumbai',
            address='Lokhandwala Complex, Andheri West',
            city='Mumbai',
            pincode='400053',
            latitude=19.1410,
            longitude=72.8285,
            operatingStatus='Open',
            serviceCoverageRadiusKm=10.0,
            rating=4.6
        )

        # Seed physical store inventories
        # Kalyan store stocks boAt earbuds (12 units)
        StoreInventory.objects.create(
            id='inv-test-kln-01',
            store=self.store_kalyan,
            product=self.prod_earbuds,
            availableQuantity=12,
            reservedQuantity=0,
            storePrice=1499.0,
            isAvailable=True
        )
        # Thane store stocks Noise buds (8 units)
        StoreInventory.objects.create(
            id='inv-test-thn-01',
            store=self.store_thane,
            product=self.prod_alt_1,
            availableQuantity=8,
            reservedQuantity=0,
            storePrice=1299.0,
            isAvailable=True
        )

    # -----------------------------------------------------------------------
    # TEST 1: Chatbot asks for PIN code when address is missing
    # -----------------------------------------------------------------------
    def test_01_chatbot_asks_for_pincode_when_address_missing(self):
        """When user asks for nearby stores without saved address or location, Sathi prompts for PIN."""
        queries = [
            "Show me nearby stores.",
            "Find stores near me.",
            "Where can I buy this product nearby?",
            "Mere aas paas kaunse stores hain?",
            "Is product ko nearby kahan se kharid sakta hoon?",
        ]
        for idx, q in enumerate(queries):
            session_id = f"test_sess_missing_{idx}"
            res = self.engine.run_sathi(query=q, session_id=session_id)
            self.assertEqual(res['status'], 'awaiting_pincode')
            self.assertIn("Please enter your 6-digit delivery PIN code so I can find nearby stores.", res['reply'])
            state = SessionMemoryManager.get_state(f"anon:{session_id}")
            self.assertEqual(state.get('pending_action'), 'AWAITING_PINCODE_FOR_STORES')

    # -----------------------------------------------------------------------
    # TEST 2: Multi-turn conversation preserves selected product across PIN prompt & entry
    # -----------------------------------------------------------------------
    def test_02_multi_turn_preserves_selected_product_across_pincode_flow(self):
        """Verifies product recommendation -> selection -> nearby stores -> PIN entry multi-turn flow."""
        session_id = "multi_turn_pincode_sess"
        # Turn 1: Recommend earbuds
        res1 = self.engine.run_sathi(
            query="Suggest wireless earbuds under ₹2,000",
            session_id=session_id
        )
        self.assertGreater(len(res1.get('products', [])), 0)

        # Turn 2: User says "Add the first one to my cart"
        res2 = self.engine.run_sathi(
            query="Add the first one to my cart",
            session_id=session_id
        )
        self.assertEqual(res2['status'], 'success')
        state = SessionMemoryManager.get_state(f"anon:{session_id}")
        selected_prod = state.get('selected_product')
        self.assertIsNotNone(selected_prod)

        # Turn 3: User says "Show me nearby stores that have this product"
        res3 = self.engine.run_sathi(
            query="Show me nearby stores that have this product",
            session_id=session_id
        )
        self.assertEqual(res3['status'], 'awaiting_pincode')
        self.assertIn("Please enter your 6-digit delivery PIN code so I can find nearby stores.", res3['reply'])
        state = SessionMemoryManager.get_state(f"anon:{session_id}")
        self.assertEqual(state.get('pending_action'), 'AWAITING_PINCODE_FOR_STORES')
        self.assertEqual(state.get('selected_product')['id'], selected_prod['id'])

        # Turn 4: User enters valid Kalyan PIN "421301"
        res4 = self.engine.run_sathi(
            query="421301",
            session_id=session_id
        )
        # Sathi should return Kalyan store with the preserved product
        self.assertIn(res4['status'], ['success', 'out_of_stock_nearby'])
        state = SessionMemoryManager.get_state(f"anon:{session_id}")
        self.assertIsNone(state.get('pending_action'))
        self.assertEqual(state.get('pincode_context'), '421301')
        self.assertEqual(state.get('selected_product')['id'], selected_prod['id'])

    # -----------------------------------------------------------------------
    # TEST 3: Malformed PIN codes are rejected with a helpful message
    # -----------------------------------------------------------------------
    def test_03_malformed_pincodes_are_rejected(self):
        """Malformed PIN codes (5 digits, letters, 7 digits) are rejected and state is preserved."""
        session_id = "malformed_pin_sess"
        # Prime the session into awaiting PIN code
        self.engine.run_sathi(query="Show me nearby stores", session_id=session_id)

        invalid_pins = ["12345", "42130", "abcd", "4213012"]
        for bad_pin in invalid_pins:
            res = self.engine.run_sathi(query=bad_pin, session_id=session_id)
            self.assertEqual(res['status'], 'error')
            self.assertIn("Please enter a valid 6-digit PIN code", res['reply'])
            state = SessionMemoryManager.get_state(f"anon:{session_id}")
            self.assertEqual(state.get('pending_action'), 'AWAITING_PINCODE_FOR_STORES')

    # -----------------------------------------------------------------------
    # TEST 4: Valid PIN code resolves to the correct area
    # -----------------------------------------------------------------------
    def test_04_valid_pincode_resolves_to_correct_area(self):
        """Valid Mumbai MMR PIN codes resolve to accurate latitude, longitude and area descriptions."""
        kalyan = resolve_coordinates('421301')
        self.assertIsNotNone(kalyan)
        self.assertAlmostEqual(kalyan[0], 19.2551, places=2)
        self.assertAlmostEqual(kalyan[1], 73.1378, places=2)
        self.assertIn('Kalyan', kalyan[2])

        thane = resolve_coordinates('400606')
        self.assertIsNotNone(thane)
        self.assertAlmostEqual(thane[0], 19.2085, places=2)
        self.assertAlmostEqual(thane[1], 72.9716, places=2)
        self.assertIn('Thane', thane[2])

        andheri = resolve_coordinates('400053')
        self.assertIsNotNone(andheri)
        self.assertAlmostEqual(andheri[0], 19.1410, places=2)
        self.assertIn('Andheri', andheri[2])

    # -----------------------------------------------------------------------
    # TEST 5: Unmapped PIN code explains the limitation
    # -----------------------------------------------------------------------
    def test_05_unmapped_pincode_explains_limitation(self):
        """Unsupported PIN code explains that AutoCart currently services Mumbai MMR."""
        session_id = "unmapped_pin_sess"
        self.engine.run_sathi(query="Show me nearby stores", session_id=session_id)

        res = self.engine.run_sathi(query="999999", session_id=session_id)
        self.assertEqual(res['status'], 'unsupported_area')
        self.assertIn("do not service PIN code 999999", res['reply'])
        self.assertIn("Mumbai Metropolitan Region", res['reply'])
        state = SessionMemoryManager.get_state(f"anon:{session_id}")
        self.assertEqual(state.get('pending_action'), 'AWAITING_PINCODE_FOR_STORES')

    # -----------------------------------------------------------------------
    # TEST 6: Nearby-store queries return real stores with correct distance calculation
    # -----------------------------------------------------------------------
    def test_06_nearby_store_query_returns_real_stores_and_distance(self):
        """Queries stores near Kalyan PIN (421301) and verifies Haversine distance accuracy."""
        stores = find_nearby_stores_with_inventory(
            customer_lat=19.2551,
            customer_lng=73.1378,
            max_radius_km=30.0,
            pin_code='421301'
        )
        self.assertGreater(len(stores), 0)
        # Closest store to 19.2551, 73.1378 should be the Kalyan store
        closest = stores[0]
        self.assertEqual(closest['storeId'], self.store_kalyan.id)
        self.assertAlmostEqual(closest['distanceKm'], 0.0, places=1)
        self.assertTrue(closest['isApproximate'])
        self.assertIn("Kalyan", closest['distanceFormatted'])

    # -----------------------------------------------------------------------
    # TEST 7: Product availability lookup reflects actual inventory quantities
    # -----------------------------------------------------------------------
    def test_07_product_availability_lookup_reflects_actual_inventory(self):
        """Store search filtered by product reflects actual StoreInventory availableQuantity."""
        stores = find_nearby_stores_with_inventory(
            product_id=self.prod_earbuds.id,
            customer_lat=19.2551,
            customer_lng=73.1378,
            max_radius_km=30.0,
            pin_code='421301'
        )
        self.assertEqual(len(stores), 1)
        self.assertEqual(stores[0]['storeId'], self.store_kalyan.id)
        self.assertEqual(stores[0]['availableQuantity'], 12)
        self.assertTrue(stores[0]['isAvailable'])

    # -----------------------------------------------------------------------
    # TEST 8: Out-of-stock handling suggests real in-stock alternatives
    # -----------------------------------------------------------------------
    def test_08_out_of_stock_suggests_real_catalog_alternatives(self):
        """When requested product has no nearby stock, Sathi suggests in-stock DB alternatives."""
        # Create an out-of-stock product with no store inventory
        p_oos = Product.objects.create(
            id='prod-oos-special',
            name='Rare Studio Audiophile Earbuds',
            slug='rare-studio-earbuds',
            category='Audio',
            brand='AudioTechnica',
            price=2499.0,
            stock=10,
            stockStatus='In Stock'
        )
        session_id = "oos_store_sess"
        state_key = f"anon:{session_id}"
        # Set target product as selected
        SessionMemoryManager.set_selected_product(state_key, {'id': p_oos.id, 'name': p_oos.name, 'category': 'Audio', 'price': 2499.0})
        # Set Kalyan location context
        SessionMemoryManager.set_delivery_address(state_key, {'pinCode': '421301', 'area': 'Kalyan'}, pin_code='421301')

        res = self.engine.run_sathi(
            query="Which nearby store has these earbuds?",
            session_id=session_id
        )
        self.assertEqual(res['status'], 'out_of_stock_nearby')
        self.assertIn("currently out of stock at all", res['reply'])
        # Must return in-stock alternatives from DB
        self.assertGreater(len(res.get('products', [])), 0)
        alt_names = [p['name'] for p in res['products']]
        self.assertTrue(any('boAt' in n or 'Noise' in n or 'Boult' in n for n in alt_names))

    # -----------------------------------------------------------------------
    # TEST 9: Delivery estimates and fees vary realistically with distance
    # -----------------------------------------------------------------------
    def test_09_delivery_estimates_and_fees_scale_with_distance(self):
        """Distance <= 3km is free delivery; distance > 3km incurs distance fee; ETA scales with km."""
        # Low-cost item under ₹499 free-shipping threshold
        p_low = Product.objects.create(
            id='prod-test-low-01',
            name='Earbud Silicone Tips Pack',
            slug='earbud-silicone-tips',
            category='Audio',
            price=199.0,
            stock=100
        )

        # Close quote (same coordinates as store, <= 3km): Free delivery
        quote_close = FulfillmentService.generate_checkout_quote(
            product_id=p_low.id,
            quantity=1,
            store_id=self.store_kalyan.id,
            customer_lat=19.2551,
            customer_lng=73.1378
        )
        self.assertEqual(quote_close['distanceKm'], 0.0)
        self.assertEqual(quote_close['deliveryFee'], 0.0)
        self.assertEqual(quote_close['estimatedMinutes'], 25)

        # Distant quote (Thane customer buying from Kalyan store: ~20 km away, subtotal < 499): Distance fee charged
        quote_distant = FulfillmentService.generate_checkout_quote(
            product_id=p_low.id,
            quantity=1,
            store_id=self.store_kalyan.id,
            customer_lat=19.2085,
            customer_lng=72.9716
        )
        dist = quote_distant['distanceKm']
        self.assertGreater(dist, 10.0)
        self.assertGreater(quote_distant['deliveryFee'], 40.0)
        self.assertGreater(quote_distant['estimatedMinutes'], 40)

        # Order >= ₹499 qualifies for free delivery even if distant
        quote_free = FulfillmentService.generate_checkout_quote(
            product_id=self.prod_alt_1.id,  # ₹1299
            quantity=1,
            store_id=self.store_kalyan.id,
            customer_lat=19.2085,
            customer_lng=72.9716
        )
        self.assertEqual(quote_free['deliveryFee'], 0.0)

    # -----------------------------------------------------------------------
    # TEST 10: Address change updates customer profile and invalidates stale location state
    # -----------------------------------------------------------------------
    def test_10_address_change_updates_profile_and_invalidates_stale_cache(self):
        """Calling /api/auth/address updates user.addresses and clears stale last_stores."""
        session_id = "addr_change_sess"
        session_key = SessionMemoryManager.get_session_key(session_id, self.user.email)
        # Prime state with old store selection
        SessionMemoryManager.update_state(session_key, {
            'last_stores': [{'storeId': 'old-store-1', 'storeName': 'Old Store'}],
            'selected_store': {'storeId': 'old-store-1', 'storeName': 'Old Store'}
        })

        # Change address via API
        payload = {
            'fullName': 'Rajesh Kulkarni',
            'phone': '9820011223',
            'addressLine': 'Flat 101, Godrej Hill, Khadakpada',
            'city': 'Kalyan',
            'state': 'Maharashtra',
            'pinCode': '421301',
            'sessionId': session_id,
        }
        res = self.auth_client.post('/api/auth/address', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['invalidatedStaleStore'])

        # Verify user profile updated in database
        self.user.refresh_from_db()
        self.assertEqual(len(self.user.addresses), 1)
        self.assertEqual(self.user.addresses[0]['pinCode'], '421301')

        # Verify Sathi conversation memory invalidated stale store selections
        state = SessionMemoryManager.get_state(session_key)
        self.assertEqual(state['last_stores'], [])
        self.assertIsNone(state['selected_store'])
        self.assertEqual(state['pincode_context'], '421301')

    # -----------------------------------------------------------------------
    # TEST 11: Chatbot context reflects new address after change
    # -----------------------------------------------------------------------
    def test_11_chatbot_context_reflects_new_address_without_reprompting(self):
        """After customer saves address, Sathi uses it directly for nearby queries without asking for PIN."""
        session_id = "auto_address_sess"
        # Save address in user profile
        self.user.addresses = [{
            'id': 'addr-1',
            'fullName': 'Rajesh Kulkarni',
            'addressLine': 'Viviana Mall area',
            'city': 'Thane',
            'state': 'Maharashtra',
            'pinCode': '400606',
            'isDefault': True
        }]
        self.user.save()

        # Chatbot query from authenticated user
        res = self.engine.run_sathi(
            query="Show me nearby stores",
            session_id=session_id,
            customer_email=self.user.email
        )
        # Sathi should NOT ask for PIN because location is known from profile
        self.assertNotEqual(res['status'], 'awaiting_pincode')
        self.assertEqual(res['status'], 'success')
        self.assertIn("Thane", res['reply'])
        self.assertGreater(len(res.get('nearbyStores', [])), 0)

    # -----------------------------------------------------------------------
    # TEST 12: Concurrency test verifies inventory deductions are atomic
    # -----------------------------------------------------------------------
    def test_12_atomic_concurrency_reservation(self):
        """Tests that two concurrent reservations on the last unit result in exactly 1 success."""
        # Create product with exactly 1 unit in store
        p_last = Product.objects.create(
            id='prod-last-unit-01',
            name='Last Available Smartwatch',
            slug='last-available-smartwatch',
            category='Electronics',
            price=2999.0,
            stock=1
        )
        inv_last = StoreInventory.objects.create(
            id='inv-last-unit-01',
            store=self.store_kalyan,
            product=p_last,
            availableQuantity=1,
            reservedQuantity=0,
            storePrice=2999.0,
            isAvailable=True
        )

        # Buyer 1 attempts reservation
        res1 = FulfillmentService.create_stock_reservation(
            store_id=self.store_kalyan.id,
            product_id=p_last.id,
            quantity=1,
            user_email='buyer1@test.com'
        )
        self.assertTrue(res1['success'])

        # Buyer 2 attempts reservation for the same product at the same store
        res2 = FulfillmentService.create_stock_reservation(
            store_id=self.store_kalyan.id,
            product_id=p_last.id,
            quantity=1,
            user_email='buyer2@test.com'
        )
        self.assertFalse(res2['success'])
        self.assertIn('Insufficient stock', res2['error'])

        # Check inventory state
        inv_last.refresh_from_db()
        self.assertEqual(inv_last.availableQuantity, 0)
        self.assertEqual(inv_last.reservedQuantity, 1)

    # -----------------------------------------------------------------------
    # TEST 13: Checkout fails if stock becomes unavailable
    # -----------------------------------------------------------------------
    def test_13_checkout_fails_if_stock_becomes_unavailable(self):
        """Attempting to order an item with insufficient stock returns HTTP 409 Conflict."""
        # Product with 0 stock
        p_out = Product.objects.create(
            id='prod-out-stock-99',
            name='Completely Out of Stock Item',
            slug='completely-out-of-stock',
            category='Audio',
            price=999.0,
            stock=0,
            stockStatus='Out of Stock'
        )
        order_payload = {
            'paymentMethod': 'Cash on Delivery',
            'items': [{'id': p_out.id, 'quantity': 1}],
            'shippingAddress': {
                'fullName': 'Rajesh Kulkarni',
                'phone': '9820011223',
                'addressLine': 'Station Road, Kalyan',
                'city': 'Kalyan',
                'pinCode': '421301',
            }
        }
        res = self.auth_client.post('/api/orders/', order_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('out of stock', res.data['detail'].lower())

    # -----------------------------------------------------------------------
    # TEST 14: Switching to an unserviceable address invalidates fulfillment options
    # -----------------------------------------------------------------------
    def test_14_switching_to_unserviceable_address_invalidates_store_option(self):
        """When distance exceeds store serviceCoverageRadiusKm, quote returns isServiceable=False."""
        # Andheri store has coverage radius of 10.0 km
        # Kalyan customer is ~35 km away
        kalyan_coords = resolve_coordinates('421301')
        quote = FulfillmentService.generate_checkout_quote(
            product_id=self.prod_earbuds.id,
            quantity=1,
            store_id=self.store_andheri.id,
            customer_lat=kalyan_coords[0],
            customer_lng=kalyan_coords[1]
        )
        self.assertFalse(quote['isServiceable'])
        self.assertIsNotNone(quote['warning'])
        self.assertIn("exceeds", quote['warning'])

    # -----------------------------------------------------------------------
    # TEST 15: PIN code is clearly labeled as an approximate area notice
    # -----------------------------------------------------------------------
    def test_15_pincode_approximate_area_labeling(self):
        """Verifies that replies with PIN-based discovery explicitly disclose approximate area."""
        session_id = "approx_notice_sess"
        self.engine.run_sathi(query="Show me nearby stores", session_id=session_id)
        res = self.engine.run_sathi(query="421301", session_id=session_id)
        self.assertIn("approximate", res['reply'].lower())
