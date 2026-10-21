"""
Regression tests for Customer Shopping Agent, Hyperlocal store routing,
PIN 400012 resolution, follow-up intents, and new order creation.
"""

from django.test import TestCase
from api.models import Product, Store, StoreInventory, Order
from api.location_service import resolve_coordinates, KNOWN_GEOCODING_DATABASE
from api.agents.engine import AgentEngine
from api.agents.memory import SessionMemoryManager

class ShoppingAgentFixesTestCase(TestCase):
    def setUp(self):
        # Create test product (Kurta under 10k)
        self.kurta1 = Product.objects.create(
            id='prod-k1',
            slug='designer-silk-kurta',
            name='Designer Silk Kurta Set',
            category='Fashion',
            price=3499.0,
            originalPrice=4999.0,
            stock=15,
            stockStatus='In Stock',
            rating=4.7
        )
        self.kurta2 = Product.objects.create(
            id='prod-k2',
            slug='cotton-chanderi-kurta',
            name='Cotton Chanderi Embroidered Kurta',
            category='Fashion',
            price=2199.0,
            originalPrice=2999.0,
            stock=20,
            stockStatus='In Stock',
            rating=4.5
        )

        # Create Powai store
        self.store_powai = Store.objects.create(
            id='store-powai-test',
            name='AutoCart Powai Store',
            address='Galleria Shopping Centre, Hiranandani, Powai',
            city='Mumbai',
            state='Maharashtra',
            pincode='400076',
            latitude=19.1195,
            longitude=72.9085,
            operatingStatus='Open'
        )

        # Create inventory for Kurta 1 at Powai store
        StoreInventory.objects.create(
            id='inv-k1-powai',
            store=self.store_powai,
            product=self.kurta1,
            availableQuantity=10,
            reservedQuantity=0
        )

        self.orchestrator = AgentEngine()
        self.session_id = 'test-session-shopping-1'

    def test_pin_400012_resolution(self):
        """PIN 400012 (Parel / Lower Parel) must resolve accurately to Mumbai coordinates."""
        res = resolve_coordinates('400012')
        self.assertIsNotNone(res)
        lat, lng, area = res
        self.assertAlmostEqual(lat, 18.9986, delta=0.01)
        self.assertAlmostEqual(lng, 72.8422, delta=0.01)
        self.assertIn('Parel', area)

    def test_kurta_search_and_recommendation(self):
        """Searching kurtas under 10k returns real products and stores recommendations in session."""
        res = self.orchestrator.run_sathi(
            query="Show me designer kurtas under 10000",
            session_id=self.session_id
        )
        self.assertEqual(res['status'], 'success')
        self.assertTrue(len(res['products']) >= 1)
        names = [p['name'] for p in res['products']]
        self.assertTrue(any('Kurta' in n for n in names))

    def test_compare_first_and_second(self):
        """Follow-up 'compare first and second' resolves the top 2 displayed products side-by-side."""
        # 1. First query
        self.orchestrator.run_sathi(
            query="Show me kurtas",
            session_id=self.session_id
        )
        # 2. Comparison follow-up
        cmp_res = self.orchestrator.run_sathi(
            query="compare first and second",
            session_id=self.session_id
        )
        self.assertEqual(cmp_res['status'], 'success')
        self.assertIn('Comparison', cmp_res['reply'])
        self.assertEqual(len(cmp_res['products']), 2)

    def test_cheapest_and_yes_confirmation(self):
        """Superlative query 'Which one is the cheapest?' followed by 'Yes' adds it to cart."""
        self.orchestrator.run_sathi(
            query="Show me kurtas",
            session_id=self.session_id
        )
        cheap_res = self.orchestrator.run_sathi(
            query="Which one is the cheapest?",
            session_id=self.session_id
        )
        self.assertIn('cheapest', cheap_res['reply'].lower())

        # Follow up with "Yes"
        yes_res = self.orchestrator.run_sathi(
            query="Yes",
            session_id=self.session_id
        )
        self.assertEqual(yes_res['status'], 'success')
        self.assertIn('Added to Cart', yes_res['reply'])
        self.assertIsNotNone(yes_res.get('cartAction'))

    def test_store_selection_and_new_order_creation(self):
        """Selecting Powai store and saying 'Order from this store' creates a Placed/Pending order."""
        # Setup session with product and nearby store
        self.orchestrator.run_sathi(
            query="Show me kurtas",
            session_id=self.session_id
        )
        session_key = SessionMemoryManager.get_session_key(self.session_id)
        SessionMemoryManager.update_state(session_key, {
            'selected_product': {
                'id': self.kurta1.id,
                'name': self.kurta1.name,
                'price': float(self.kurta1.price)
            },
            'selected_store': {
                'storeId': self.store_powai.id,
                'storeName': self.store_powai.name,
                'address': self.store_powai.address,
                'city': self.store_powai.city,
                'pincode': self.store_powai.pincode
            },
            'last_stores': [{
                'storeId': self.store_powai.id,
                'storeName': self.store_powai.name,
                'address': self.store_powai.address,
                'city': self.store_powai.city,
                'pincode': self.store_powai.pincode
            }]
        })

        order_res = self.orchestrator.run_sathi(
            query="Order from this store",
            session_id=self.session_id
        )
        self.assertEqual(order_res['status'], 'success')
        self.assertIn('Order Placed', order_res['reply'])
        order_action = order_res.get('orderAction')
        self.assertIsNotNone(order_action)
        new_order_id = order_action['orderId']

        # Verify created order in database: status must be Placed and payment Pending!
        created_order = Order.objects.get(id=new_order_id)
        self.assertEqual(created_order.status, 'Placed')
        self.assertEqual(created_order.paymentStatus, 'Pending')
        self.assertEqual(created_order.paymentMethod, 'Cash on Delivery')
        self.assertEqual(created_order.shippingAddress['storeName'], 'AutoCart Powai Store')
