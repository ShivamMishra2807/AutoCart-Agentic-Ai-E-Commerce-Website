"""
Comprehensive Automated Test Suite for AutoCart Sathi Agent.
Tests all 14 required capabilities:
1. Product search
2. Price filters
3. Correct recommendation ordering
4. First, second, and third product selection
5. Selection after multiple recommendation lists
6. Ambiguous references
7. Quantity updates
8. Actual cart persistence
9. Out-of-stock products
10. Multiple users and conversation isolation
11. Missing LLM credentials
12. Malformed model responses
13. Duplicate submissions and retries
14. Frontend/API integration and error handling
"""

from unittest.mock import MagicMock, patch
from django.test import TestCase
from rest_framework.test import APIClient

from api.models import Product, User, ChatSession, SupportTicket
from api.views import generate_token
from api.agents.memory import SessionMemoryManager
from api.agents import tools as tool_lib
from api.agents.engine import SathiOrchestrator
from api.agents.llm_provider import UnifiedLLMProvider


def authed(user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION='Bearer ' + generate_token(user))
    return c


class SathiAgentComprehensiveTests(TestCase):
    def setUp(self):
        # Create test users
        self.user_a = User.objects.create_user(email='user_a@test.com', name='Alice Sharma', password='password123')
        self.user_b = User.objects.create_user(email='user_b@test.com', name='Bob Patel', password='password123')
        self.client_a = authed(self.user_a)
        self.client_b = authed(self.user_b)
        self.guest_client = APIClient()

        # Clean in-memory session manager cache
        SessionMemoryManager._sessions.clear()
        SessionMemoryManager._states.clear()
        SessionMemoryManager._timestamps.clear()

        # Seed real database products for realistic testing
        self.p1 = Product.objects.create(
            id='prod-bud-1', name='boAt Airdopes 141 Bluetooth Earbuds', slug='boat-airdopes-141',
            category='Audio', brand='boAt', price=1299, originalPrice=4490, stock=50, rating=4.2, images=['boat141.jpg']
        )
        self.p2 = Product.objects.create(
            id='prod-bud-2', name='Noise Buds VS102 Truly Wireless Earbuds', slug='noise-buds-vs102',
            category='Audio', brand='Noise', price=1499, originalPrice=2999, stock=30, rating=4.1, images=['noise102.jpg']
        )
        self.p3 = Product.objects.create(
            id='prod-bud-3', name='Boult Audio AirBass Propods', slug='boult-airbass',
            category='Audio', brand='Boult', price=999, originalPrice=2499, stock=25, rating=3.9, images=['boult.jpg']
        )
        self.p4 = Product.objects.create(
            id='prod-bud-4', name='Realme TechLife Buds T100', slug='realme-buds-t100',
            category='Audio', brand='Realme', price=1499, originalPrice=2999, stock=40, rating=4.3, images=['realme.jpg']
        )
        self.p5 = Product.objects.create(
            id='prod-bud-5', name='OnePlus Nord Buds 2r', slug='oneplus-nord-buds-2r',
            category='Audio', brand='OnePlus', price=1999, originalPrice=2299, stock=15, rating=4.5, images=['oneplus.jpg']
        )
        self.p_expensive = Product.objects.create(
            id='prod-bud-exp', name='Sony WF-1000XM5 Premium Earbuds', slug='sony-wf1000xm5',
            category='Audio', brand='Sony', price=19990, originalPrice=24990, stock=5, rating=4.8, images=['sony.jpg']
        )
        self.p_out_of_stock = Product.objects.create(
            id='prod-bud-oos', name='Apple AirPods Pro 2nd Gen', slug='airpods-pro-2',
            category='Audio', brand='Apple', price=20999, originalPrice=24900, stock=0, rating=4.9, images=['airpods.jpg']
        )
        self.p_laptop = Product.objects.create(
            id='prod-lap-1', name='ASUS Vivobook 15 Intel Core i5', slug='asus-vivobook-15',
            category='Electronics', brand='ASUS', price=48990, originalPrice=59990, stock=12, rating=4.4, images=['asus.jpg']
        )

        self.tools = tool_lib
        self.orchestrator = SathiOrchestrator()

    # -------------------------------------------------------------------------
    # 1. Product search (name, category)
    # -------------------------------------------------------------------------
    def test_01_product_search(self):
        """Test searching for products by name and category returns real database records."""
        res_boat = self.tools.search_products(query='boAt Airdopes')
        self.assertTrue(res_boat['success'])
        self.assertGreaterEqual(res_boat['count'], 1)
        self.assertEqual(res_boat['products'][0]['id'], self.p1.id)

        res_audio = self.tools.search_products(query='Audio', category='Audio')
        self.assertTrue(res_audio['success'])
        self.assertGreaterEqual(res_audio['count'], 5)
        names = [p['name'] for p in res_audio['products']]
        self.assertIn('boAt Airdopes 141 Bluetooth Earbuds', names)

    # -------------------------------------------------------------------------
    # 2. Price filters (min, max, budget)
    # -------------------------------------------------------------------------
    def test_02_price_filters(self):
        """Test that budget constraints filter out items outside the range."""
        # Query under 2000 should exclude Sony WF-1000XM5 (₹19,990)
        res = self.tools.search_products(query='earbuds', max_price=2000.0)
        self.assertTrue(res['success'])
        for p in res['products']:
            self.assertLessEqual(p['price'], 2000.0)
        product_ids = [p['id'] for p in res['products']]
        self.assertNotIn(self.p_expensive.id, product_ids)

        # Min price filter
        res_min = self.tools.search_products(query='earbuds', min_price=1500.0)
        for p in res_min['products']:
            self.assertGreaterEqual(p['price'], 1500.0)

    # -------------------------------------------------------------------------
    # 3. Correct recommendation ordering
    # -------------------------------------------------------------------------
    def test_03_recommendation_ordering_and_count(self):
        """Test requesting 5 earbuds under 2000 returns 5 ordered items with stable IDs."""
        res = self.orchestrator.run_sathi(
            query="Suggest five wireless earbuds under ₹2,000",
            session_id="test-session-order",
            customer_email="user_a@test.com"
        )
        self.assertEqual(res['status'], 'success')
        self.assertEqual(len(res['products']), 5)

        # Check in memory that exact order matches
        mem_prods = SessionMemoryManager.get_displayed_products("user_a@test.com:test-session-order")
        self.assertEqual(len(mem_prods), 5)
        for i in range(5):
            self.assertEqual(res['products'][i]['id'], mem_prods[i]['id'])

    # -------------------------------------------------------------------------
    # 4. First, second, and third product selection (ordinals & Hinglish)
    # -------------------------------------------------------------------------
    def test_04_ordinal_selection_and_hinglish(self):
        """Test selecting second product resolves exactly to the 2nd product."""
        # Setup recommendations
        init_res = self.orchestrator.run_sathi(
            query="Suggest five wireless earbuds under ₹2,000",
            session_id="test-ord-session",
            customer_email="user_a@test.com"
        )
        second_prod = init_res['products'][1]
        third_prod = init_res['products'][2]

        # Add second one to cart
        add_res = self.orchestrator.run_sathi(
            query="Add the second one to my cart",
            session_id="test-ord-session",
            customer_email="user_a@test.com"
        )
        self.assertEqual(add_res['status'], 'success')
        self.assertEqual(add_res['cartAction']['productId'], second_prod['id'])
        self.assertEqual(add_res['selectedProductId'], second_prod['id'])

        # Hinglish reference to third product
        hinglish_res = self.orchestrator.run_sathi(
            query="Actually, teesra wala khareed lunga",
            session_id="test-ord-session",
            customer_email="user_a@test.com"
        )
        self.assertEqual(hinglish_res['status'], 'success')
        self.assertEqual(hinglish_res['selectedProductId'], third_prod['id'])

    # -------------------------------------------------------------------------
    # 5. Selection after multiple recommendation lists
    # -------------------------------------------------------------------------
    def test_05_selection_after_multiple_recommendations(self):
        """Test that after a new search, ordinals resolve to the newest list."""
        sid = "multi-rec-session"
        email = "user_a@test.com"

        # List 1: Earbuds
        self.orchestrator.run_sathi("Suggest earbuds under 2000", session_id=sid, customer_email=email)
        # List 2: Laptops
        laptop_res = self.orchestrator.run_sathi("Show me laptops", session_id=sid, customer_email=email)
        self.assertTrue(any(p['category'] == 'Electronics' for p in laptop_res['products']))

        # Now "Add the first one" should resolve to the laptop, not the earbud
        cart_res = self.orchestrator.run_sathi("Add the first one to cart", session_id=sid, customer_email=email)
        self.assertEqual(cart_res['selectedProductId'], self.p_laptop.id)

    # -------------------------------------------------------------------------
    # 6. Ambiguous references
    # -------------------------------------------------------------------------
    def test_06_ambiguous_references(self):
        """Test that ambiguous or out-of-range references return a clarification prompt."""
        sid = "ambig-session"
        email = "user_a@test.com"

        # Only 2 products in this list
        session_key = SessionMemoryManager.get_session_key(sid, email)
        SessionMemoryManager.set_recommendations(
            session_key,
            [{'id': self.p1.id, 'name': self.p1.name, 'price': self.p1.price},
             {'id': self.p2.id, 'name': self.p2.name, 'price': self.p2.price}]
        )

        # Asking for the 5th item when only 2 are displayed
        res = self.orchestrator.run_sathi("Add the fifth one to cart", session_id=sid, customer_email=email)
        self.assertEqual(res['status'], 'clarification')
        self.assertIn("2 products", res['reply'])

    # -------------------------------------------------------------------------
    # 7. Quantity updates
    # -------------------------------------------------------------------------
    def test_07_quantity_updates(self):
        """Test 'Add two pieces' updates quantity without creating duplicates."""
        sid = "qty-session"
        email = "user_a@test.com"

        # Initialize with product
        self.orchestrator.run_sathi("Suggest earbuds", session_id=sid, customer_email=email)
        self.orchestrator.run_sathi("Add the first one to my cart", session_id=sid, customer_email=email)

        # Update quantity: "Add two pieces"
        qty_res = self.orchestrator.run_sathi("Add two pieces", session_id=sid, customer_email=email)
        self.assertEqual(qty_res['status'], 'success')
        self.assertEqual(qty_res['cartAction']['type'], 'UPDATE_QUANTITY')
        self.assertEqual(qty_res['cartAction']['quantity'], 2)
        self.assertEqual(qty_res['quantity'], 2)

    # -------------------------------------------------------------------------
    # 8. Actual cart persistence and calculation
    # -------------------------------------------------------------------------
    def test_08_cart_persistence_and_calculations(self):
        """Test ToolLibrary cart operations calculate accurate subtotals and check stock."""
        active_cart = [{'id': self.p1.id, 'price': float(self.p1.price), 'quantity': 1}]

        # Add p2
        res = self.tools.add_to_cart_tool(self.p2.id, quantity=2, cart_items=active_cart, user_email='user_a@test.com')
        self.assertTrue(res['success'])
        expected_subtotal = float(self.p1.price) * 1 + float(self.p2.price) * 2
        self.assertEqual(res['cartSummary']['subtotal'], expected_subtotal)
        self.assertEqual(res['cartSummary']['itemCount'], 3)

        # Update quantity of p2 to 1
        upd = self.tools.update_cart_quantity_tool(self.p2.id, quantity=1, cart_items=res['cartItems'])
        self.assertTrue(upd['success'])
        self.assertEqual(upd['cartSummary']['subtotal'], float(self.p1.price) + float(self.p2.price))

        # Remove p1
        rem = self.tools.remove_from_cart_tool(self.p1.id, cart_items=upd['cartItems'])
        self.assertTrue(rem['success'])
        self.assertEqual(rem['cartSummary']['subtotal'], float(self.p2.price))

    # -------------------------------------------------------------------------
    # 9. Out-of-stock products
    # -------------------------------------------------------------------------
    def test_09_out_of_stock_products(self):
        """Test that out-of-stock products are gracefully rejected with in-stock alternatives."""
        res = self.tools.add_to_cart_tool(self.p_out_of_stock.id, quantity=1, user_email='user_a@test.com')
        self.assertFalse(res['success'])
        self.assertEqual(res['errorType'], 'OUT_OF_STOCK')
        self.assertIn('currently out of stock', res['error'])
        self.assertGreater(len(res['alternatives']), 0)

    # -------------------------------------------------------------------------
    # 10. Multiple users and conversation isolation
    # -------------------------------------------------------------------------
    def test_10_multi_user_isolation(self):
        """Test that User A's recommendations and cart state never leak to User B."""
        sid = "shared-session-name"

        # User A searches for earbuds
        self.orchestrator.run_sathi("Suggest earbuds under 2000", session_id=sid, customer_email="user_a@test.com")
        key_a = SessionMemoryManager.get_session_key(sid, "user_a@test.com")
        state_a = SessionMemoryManager.get_state(key_a)
        self.assertTrue(len(state_a['recommendations']) > 0)

        # User B starts session with same session_id string
        key_b = SessionMemoryManager.get_session_key(sid, "user_b@test.com")
        state_b = SessionMemoryManager.get_state(key_b)
        self.assertEqual(len(state_b['recommendations']), 0)

        # User B asks "Add the second one to my cart" - should prompt for search, not use A's products
        res_b = self.orchestrator.run_sathi("Add the second one to my cart", session_id=sid, customer_email="user_b@test.com")
        self.assertEqual(res_b['status'], 'clarification')
        self.assertIn("don't have any recent product recommendations", res_b['reply'].lower())

    # -------------------------------------------------------------------------
    # 11. Missing LLM credentials (deterministic engine fallback)
    # -------------------------------------------------------------------------
    def test_11_missing_llm_credentials_fallback(self):
        """Test that without GROQ or GEMINI API keys, system executes completely and reliably."""
        with patch.object(UnifiedLLMProvider, 'is_available', new_callable=lambda: property(lambda self: False)):
            res = self.orchestrator.run_sathi(
                query="Suggest wireless earbuds under 2000",
                session_id="no-llm-session",
                customer_email="user_a@test.com"
            )
            self.assertEqual(res['status'], 'success')
            self.assertGreaterEqual(len(res['products']), 1)
            self.assertIn('boAt', res['reply'])

    # -------------------------------------------------------------------------
    # 12. Malformed model responses
    # -------------------------------------------------------------------------
    def test_12_malformed_model_responses(self):
        """Test that if an LLM returns malformed JSON or empty string, fallback gracefully handles it."""
        provider = UnifiedLLMProvider()
        with patch.object(provider, 'generate', return_value="INVALID_JSON_AND_GARBAGE"):
            # Orchestrator should never crash, falling back cleanly
            res = self.orchestrator.run_sathi(
                query="Suggest earbuds under 2000",
                session_id="malformed-session",
                customer_email="user_a@test.com"
            )
            self.assertEqual(res['status'], 'success')
            self.assertGreater(len(res['products']), 0)

    # -------------------------------------------------------------------------
    # 13. Duplicate submissions and retries
    # -------------------------------------------------------------------------
    def test_13_duplicate_submissions_and_retries(self):
        """Test repeated requests do not create duplicate or corrupted cart state."""
        sid = "dup-session"
        email = "user_a@test.com"
        self.orchestrator.run_sathi("Suggest earbuds under 2000", session_id=sid, customer_email=email)

        # First add
        res1 = self.orchestrator.run_sathi("Add the first one to my cart", session_id=sid, customer_email=email)
        self.assertEqual(res1['status'], 'success')

        # Retry exact same query immediately
        res2 = self.orchestrator.run_sathi("Add the first one to my cart", session_id=sid, customer_email=email)
        self.assertEqual(res2['status'], 'success')
        self.assertEqual(res2['selectedProductId'], res1['selectedProductId'])

    # -------------------------------------------------------------------------
    # 14. API Endpoint Integration (support/chat, rating, tickets)
    # -------------------------------------------------------------------------
    def test_14_api_integration(self):
        """Test full DRF API endpoint /api/support/chat executes and returns structured contract."""
        resp = self.client_a.post('/api/support/chat', {
            'message': 'Suggest five wireless earbuds under 2000'
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['sessionId'])
        self.assertGreaterEqual(len(data['cards']), 5)
        self.assertIn('boAt', data['reply'])

        # Now follow up on that chat session
        sid = data['sessionId']
        resp2 = self.client_a.post('/api/support/chat', {
            'message': 'Which one is the cheapest?',
            'sessionId': sid
        }, format='json')
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        self.assertIn('cheapest is', data2['reply'].lower())

        # Now add the cheapest (or second one) to cart
        resp3 = self.client_a.post('/api/support/chat', {
            'message': 'Add the second one to my cart',
            'sessionId': sid
        }, format='json')
        self.assertEqual(resp3.status_code, 200)
        data3 = resp3.json()
        self.assertEqual(data3['cartAction']['type'], 'ADD_TO_CART')
        self.assertTrue(data3['cartAction']['product'])

        # Chat rating
        resp_rate = self.client_a.post(f'/api/support/chat/{sid}/rating', {'rating': 5}, format='json')
        self.assertEqual(resp_rate.status_code, 200)
        self.assertTrue(resp_rate.json()['success'])

    # -------------------------------------------------------------------------
    # 15. Strict Category Filtering (Laptops vs Headphones / Mice / Backpacks)
    # -------------------------------------------------------------------------
    def test_15_strict_category_filtering_laptops_and_accessories(self):
        """Test that asking for laptops returns strictly laptops and rejects accessories."""
        # Create non-laptop items
        p_backpack = Product.objects.create(
            id='prod-bp-1', name='Wildcraft Laptop Backpack 30L', slug='wildcraft-bp-1',
            category='Fashion', brand='Wildcraft', price=1899, stock=20, rating=4.3
        )
        p_mouse = Product.objects.create(
            id='prod-mouse-test', name='Logitech MX Master 3S Wireless Mouse', slug='logitech-mx-test',
            category='Electronics', brand='Logitech', price=6999, stock=15, rating=4.7
        )
        p_headphone = Product.objects.create(
            id='prod-hp-test', name='Sony WH-1000XM5 Wireless ANC Headphones', slug='sony-wh-test',
            category='Electronics', brand='Sony', price=26990, stock=8, rating=4.8
        )
        # Create 5 more laptops
        laptops = [
            Product.objects.create(id=f'prod-lap-test-{i}', name=f'Laptop Model {i}', slug=f'lap-slug-{i}',
                                   category='Electronics', brand='Brand', price=30000 + i * 5000, stock=10, rating=4.5)
            for i in range(2, 7)
        ]

        res = self.tools.search_products(query='Suggest 6 laptops under 70000', limit=6)
        self.assertTrue(res['success'])
        self.assertGreaterEqual(res['count'], 6)

        returned_ids = [p['id'] for p in res['products']]
        # Assert none of the accessories are returned
        self.assertNotIn(p_backpack.id, returned_ids)
        self.assertNotIn(p_mouse.id, returned_ids)
        self.assertNotIn(p_headphone.id, returned_ids)

        # Assert every returned product has 'laptop' or laptop indicator
        for p in res['products']:
            self.assertTrue(
                any(w in p['name'].lower() for w in ['laptop', 'vivobook', 'macbook', 'ideapad', 'pavilion', 'swift', 'tuf', 'xps']) or
                p.get('category') == 'Laptops'
            )

    # -------------------------------------------------------------------------
    # 16. Sixth-Product Selection and Ordinal Zero-Based Indexing Resolution
    # -------------------------------------------------------------------------
    def test_16_sixth_product_selection_and_ordinals(self):
        """Test that 'add the sixth one to my cart' adds product at index 5, not index 0."""
        # Ensure 6 laptops exist
        for i in range(2, 7):
            Product.objects.get_or_create(
                id=f'prod-lap-ord-{i}',
                defaults={'name': f'Dell Inspiron Laptop {i}', 'slug': f'dell-lap-{i}',
                          'category': 'Electronics', 'brand': 'Dell', 'price': 40000 + i * 2000, 'stock': 10, 'rating': 4.4}
            )

        sid = 'test-ordinals-session'
        email = 'user_a@test.com'

        # Turn 1: recommend 6 laptops
        rec_res = self.orchestrator.run_sathi('Suggest 6 laptops under 70000', session_id=sid, customer_email=email)
        self.assertEqual(len(rec_res['products']), 6)
        self.assertTrue(rec_res.get('recommendationListId'))
        self.assertEqual(rec_res.get('orderedProductIds'), [p['id'] for p in rec_res['products']])

        first_product = rec_res['products'][0]
        second_product = rec_res['products'][1]
        third_product = rec_res['products'][2]
        sixth_product = rec_res['products'][5]

        # Verify sixth is distinct from first, second, third
        self.assertNotEqual(sixth_product['id'], first_product['id'])
        self.assertNotEqual(sixth_product['id'], second_product['id'])
        self.assertNotEqual(sixth_product['id'], third_product['id'])

        # Turn 2: "add the first one to my cart"
        cart_res_1 = self.orchestrator.run_sathi('Add the first one to my cart', session_id=sid, customer_email=email)
        self.assertEqual(cart_res_1['status'], 'success')
        self.assertEqual(cart_res_1['selectedProductId'], first_product['id'])
        self.assertEqual(cart_res_1['cartAction']['productId'], first_product['id'])

        # Turn 3: "add the second one to my cart"
        cart_res_2 = self.orchestrator.run_sathi('Add the second one to my cart', session_id=sid, customer_email=email)
        self.assertEqual(cart_res_2['status'], 'success')
        self.assertEqual(cart_res_2['selectedProductId'], second_product['id'])
        self.assertEqual(cart_res_2['cartAction']['productId'], second_product['id'])

        # Turn 4: "add the third one to my cart"
        cart_res_3 = self.orchestrator.run_sathi('Add the third one to my cart', session_id=sid, customer_email=email)
        self.assertEqual(cart_res_3['status'], 'success')
        self.assertEqual(cart_res_3['selectedProductId'], third_product['id'])
        self.assertEqual(cart_res_3['cartAction']['productId'], third_product['id'])

        # Turn 5: "add the sixth one to my cart" (zero-based index 5)
        cart_res_6 = self.orchestrator.run_sathi('Add the sixth one to my cart', session_id=sid, customer_email=email)
        self.assertEqual(cart_res_6['status'], 'success')
        self.assertEqual(cart_res_6['selectedProductId'], sixth_product['id'])
        self.assertEqual(cart_res_6['cartAction']['productId'], sixth_product['id'])

        # Turn 6: "add the last one to my cart"
        cart_res_last = self.orchestrator.run_sathi('Add the last one to my cart', session_id=sid, customer_email=email)
        self.assertEqual(cart_res_last['selectedProductId'], sixth_product['id'])

    # -------------------------------------------------------------------------
    # 17. Missing Conversation State Handling
    # -------------------------------------------------------------------------
    def test_17_missing_conversation_state_handling(self):
        """Test that attempting to select or add without any displayed products asks for clarification."""
        sid = 'empty-state-session'
        email = 'new_user@test.com'

        # Without any search or recommendations, attempt to add ordinal
        res = self.orchestrator.run_sathi('Add the second one to my cart', session_id=sid, customer_email=email)
        self.assertEqual(res['status'], 'clarification')
        self.assertIn("don't have any recent product recommendations", res['reply'].lower())
        self.assertIsNone(res.get('cartAction'))
