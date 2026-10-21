"""What each role can see: sellers see only their own business, admins see the marketplace, customers see neither."""

from django.test import TestCase
from rest_framework.test import APIClient

from api.models import Enquiry, Order, Product, SellerApplication, SupportTicket, User
from api.views import generate_token


def authed(user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION='Bearer ' + generate_token(user))
    return c


class RoleViewTests(TestCase):
    def setUp(self):
        mk = lambda e, n, r='CUSTOMER': User.objects.create_user(email=e, name=n, password='pw-12345', role=r)  # noqa: E731
        self.cust = mk('cust@example.com', 'Cathy Customer')
        self.s1 = mk('s1@example.com', 'Sita One', 'SELLER')
        self.s2 = mk('s2@example.com', 'Ravi Two', 'SELLER')
        self.pending = mk('pending@example.com', 'Pia Pending', 'SELLER')  # role set but never approved
        self.admin = mk('boss@example.com', 'Boss', 'ADMIN')
        for u, name in ((self.s1, 'Sita Stores'), (self.s2, 'Ravi Mart')):
            SellerApplication.objects.create(id=f'app-{u.id}', ownerUserId=u.id, applicantName=u.name, companyName=name, email=u.email, phone='9820012345', status='APPROVED')
        Product.objects.create(id='a1', name='Flask', slug='flask', category='Home', seller='Sita Stores', price=500, originalPrice=800, stock=3, specifications={'Capacity': '1 litre', 'Material': 'Steel'})
        Product.objects.create(id='a2', name='Bottle', slug='bottle', category='Home', seller='Sita Stores', price=200, stock=50)
        Product.objects.create(id='b1', name='Rival Lamp', slug='lamp', category='Home', seller='Ravi Mart', price=900, stock=0)
        Order.objects.create(id='ORD-1', customerName='Cathy Customer', customerEmail='cust@example.com', date='2026-01-01', status='Confirmed',
                             items=[{'id': 'a1', 'name': 'Flask', 'price': 500, 'quantity': 2}, {'id': 'b1', 'name': 'Rival Lamp', 'price': 900, 'quantity': 1}])
        self.c, self.a, self.b, self.p, self.boss, self.guest = authed(self.cust), authed(self.s1), authed(self.s2), authed(self.pending), authed(self.admin), APIClient()

    def test_seller_overview_is_only_for_active_sellers(self):
        self.assertEqual(self.guest.get('/api/seller/overview').status_code, 401)
        self.assertEqual(self.c.get('/api/seller/overview').status_code, 403)
        self.assertEqual(self.boss.get('/api/seller/overview').status_code, 403)  # even the admin does not get a seller's view
        self.assertEqual(self.p.get('/api/seller/overview').status_code, 403)

    def test_a_seller_sees_only_their_own_business(self):
        d = self.a.get('/api/seller/overview').json()
        self.assertEqual((d['company'], d['productsCount'], d['lowStock'], d['unitsSold'], d['revenue']), ('Sita Stores', 2, 1, 2, 1000))
        self.assertEqual([p['id'] for p in d['products']].sort(), ['a1', 'a2'].sort())
        self.assertNotIn('Rival Lamp', str(d))  # the other seller's product in the same order is not shown
        self.assertEqual(d['orders'][0]['customerFirstName'], 'Cathy')
        self.assertNotIn('cust@example.com', str(d))
        other = self.b.get('/api/seller/overview').json()
        self.assertEqual((other['company'], other['productsCount'], other['outOfStock']), ('Ravi Mart', 1, 1))
        self.assertNotIn('Flask', str(other))

    def test_seller_can_change_own_price_and_stock_only(self):
        res = self.a.patch('/api/seller/products/a1', {'price': 400, 'stock': 20}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual((res.json()['discount'], res.json()['stockStatus']), (50, 'In Stock'))
        self.assertEqual(self.a.patch('/api/seller/products/b1', {'stock': 99}, format='json').status_code, 404)  # someone else's product
        self.assertEqual(self.a.patch('/api/seller/products/a1', {'price': -5, 'stock': 'x'}, format='json').status_code, 400)
        self.assertEqual(self.c.patch('/api/seller/products/a1', {'stock': 9}, format='json').status_code, 403)
        self.assertEqual(Product.objects.get(id='b1').stock, 0)

    def test_admin_overview_is_admin_only_and_counts_real_things(self):
        self.assertEqual(self.a.get('/api/admin/overview').status_code, 403)
        self.assertEqual(self.c.get('/api/admin/overview').status_code, 403)
        SellerApplication.objects.create(id='app-new', ownerUserId='x', applicantName='N', companyName='New Shop', email='n@example.com', phone='1', status='PENDING_ADMIN_APPROVAL', riskScore=40)
        Enquiry.objects.create(id='ENQ-1', customerName='A', customerEmail='a@example.com', message='Is this good?')
        SupportTicket.objects.create(id='TKT-1', customerEmail='cust@example.com', subject='Late')
        d = self.boss.get('/api/admin/overview').json()
        self.assertEqual((d['cards']['applications'], d['cards']['openEnquiries'], d['cards']['openTickets'], d['cards']['outOfStock'], d['cards']['lowStock']), (1, 1, 1, 1, 1))
        text = ' '.join(b['text'] for b in d['briefing'])
        self.assertIn('New Shop', text)
        self.assertIn('Flask', text)

    def test_answer_draft_uses_only_the_products_own_details(self):
        enq = Enquiry.objects.create(id='ENQ-2', productId='a1', productName='Flask', sellerName='Sita Stores', customerName='Anita Rao', customerEmail='a@example.com', message='What is the capacity and do you have it in stock?')
        d = self.a.post('/api/enquiries/ENQ-2/draft').json()
        self.assertIn('1 litre', d['draft'])
        self.assertIn('3 in stock', d['draft'])
        self.assertEqual(d['confidence'], 'high')
        self.assertEqual(self.b.post('/api/enquiries/ENQ-2/draft').status_code, 404)  # a rival seller cannot see it
        self.assertEqual(self.c.post('/api/enquiries/ENQ-2/draft').status_code, 404)
        enq.message = 'Will it survive a trip to Mars?'
        enq.save()
        self.assertEqual(self.a.post('/api/enquiries/ENQ-2/draft').json()['confidence'], 'low')


class SellerAssistantTests(RoleViewTests):
    """The seller assistant answers from the seller's own rows only."""

    def ask(self, client, q):
        return client.post('/api/seller/assistant', {'message': q}, format='json')

    def test_only_active_sellers_can_ask(self):
        for client, code in ((self.guest, 401), (self.c, 403), (self.boss, 403), (self.p, 403)):
            self.assertEqual(self.ask(client, 'low stock').status_code, code)

    def test_low_stock_and_sales_come_from_the_database(self):
        low = self.ask(self.a, 'Which products are low on stock?').json()
        self.assertEqual(low['rows'], [['Flask', 3]])
        best = self.ask(self.a, 'What are my best selling products?').json()
        self.assertEqual(best['rows'][0][:2], ['Flask', 2])
        self.assertIn('1,000', self.ask(self.a, 'What is my revenue?').json()['answer'])

    def test_it_never_shows_another_sellers_product(self):
        d = self.ask(self.a, 'tell me about Rival Lamp and all stock').json()
        self.assertNotIn('Rival', str(d))

    def test_empty_question_is_rejected(self):
        self.assertEqual(self.ask(self.a, '  ').status_code, 400)


class SellerCreateProductTests(RoleViewTests):
    def test_seller_adds_a_product_with_no_fake_reviews(self):
        r = self.a.post('/api/seller/products', {'name': 'Steel Tiffin', 'category': 'Home', 'price': '350', 'stock': '12'}, format='json')
        self.assertEqual(r.status_code, 201)
        p = Product.objects.get(id=r.json()['id'])
        self.assertEqual((p.seller, p.rating, p.reviewCount, p.stock), ('Sita Stores', 0, 0, 12))

    def test_bad_input_and_wrong_roles(self):
        self.assertEqual(self.a.post('/api/seller/products', {'name': 'x', 'price': '-1', 'stock': 'a'}, format='json').status_code, 400)
        self.assertEqual(self.c.post('/api/seller/products', {'name': 'Steel Tiffin', 'category': 'Home', 'price': 5, 'stock': 1}, format='json').status_code, 403)
        self.assertEqual(self.guest.post('/api/seller/products', {}, format='json').status_code, 401)


class DashboardAndMemoryTests(RoleViewTests):
    def test_overview_has_chart_data_and_commission(self):
        d = self.a.get('/api/seller/overview').json()
        self.assertEqual(len(d['salesByDay']), 30)
        self.assertEqual(d['earnings'], {'gross': 1000, 'commission': 60, 'youKeep': 940})  # 'Home' is not a listed category, so the 6% default applies
        self.assertEqual(d['topProducts'][0]['name'], 'Flask')

    def test_commission_terms_are_public(self):
        t = APIClient().get('/api/commission').json()
        self.assertEqual((t['joiningFee'], t['listingFee'], t['monthlyFee']), (0, 0, 0))

    def test_chat_uses_the_name_and_remembers_then_forgets(self):
        r = self.c.post('/api/support/chat', {'message': 'show me a laptop under 50000'}, format='json').json()
        self.assertIn('Cathy', r['reply'])
        mem = self.c.get('/api/support/memory').json()
        self.assertEqual((mem['budgetMax'], 'Electronics' in mem['interests']), (50000, True))
        self.c.delete('/api/support/memory')
        self.assertEqual(self.c.get('/api/support/memory').json()['interests'], [])
        self.assertEqual(self.guest.get('/api/support/memory').status_code, 401)


class AgentOrdersRiskTests(RoleViewTests):
    def test_langgraph_agent_searches_with_budget_and_buys_by_reference(self):
        from api import agent_graph
        r = agent_graph.run('flask under 600')
        self.assertEqual([p['id'] for p in r['products']], ['a1'])
        r = agent_graph.run('buy the first one', last_cards=[{'type': 'product', 'id': 'a1'}])
        self.assertEqual(r['buyProductId'], 'a1')
        self.assertEqual(agent_graph.run('buy the first one')['buyProductId'], '')  # nothing to refer to: it asks which product
        self.assertEqual(agent_graph.run('how does delivery work')['intent'], 'faq')

    def test_chat_returns_buy_id_and_cards(self):
        r = self.c.post('/api/support/chat', {'message': 'flask under 600'}, format='json').json()
        self.assertEqual([c['id'] for c in r['cards']], ['a1'])
        r2 = self.c.post('/api/support/chat', {'message': 'buy the first one', 'sessionId': r['sessionId']}, format='json').json()
        self.assertEqual(r2['buyProductId'], 'a1')

    def test_seller_packs_only_their_own_order_and_sees_the_route(self):
        Order.objects.filter(id='ORD-1').update(shippingAddress={'addressLine': '12 Hill Rd', 'city': 'Mumbai', 'latitude': 19.07, 'longitude': 72.87})
        app = SellerApplication.objects.get(ownerUserId=self.s1.id)
        app.storeLatitude, app.storeLongitude, app.storeName = 19.12, 72.84, 'Sita Store'
        app.save()
        route = self.a.get('/api/seller/orders/ORD-1/route').json()
        self.assertEqual((route['pickup']['name'], route['drop']['lat']), ('Sita Store', 19.07))
        self.assertGreater(route['straightLineKm'], 1)
        self.assertEqual(self.b.get('/api/seller/orders/ORD-1/route').status_code, 200)  # Ravi's product is in this order too
        self.assertEqual(self.a.post('/api/seller/orders/ORD-1/pack').json()['status'], 'Packed')
        self.assertEqual(self.a.post('/api/seller/orders/ORD-1/pack').status_code, 400)  # already packed
        self.assertEqual(self.c.post('/api/seller/orders/ORD-1/pack').status_code, 403)
        Order.objects.create(id='ORD-2', customerName='X', customerEmail='x@example.com', date='2026-01-02', items=[{'id': 'b1', 'name': 'Rival Lamp', 'price': 900, 'quantity': 1}])
        self.assertEqual(self.a.post('/api/seller/orders/ORD-2/pack').status_code, 404)  # not Sita's order

    def test_admin_overview_lists_pending_sellers_with_risk(self):
        SellerApplication.objects.create(id='app-new', applicantName='Nina New', companyName='Nina Mart', email='n@example.com', phone='9820000000',
                                         status='PENDING_ADMIN_APPROVAL', riskScore=62, riskCategory='High', city='Mumbai')
        d = self.boss.get('/api/admin/overview').json()
        a = d['applications'][0]
        self.assertEqual((a['company'], a['riskScore'], a['riskCategory'], a['trustScore']), ('Nina Mart', 62, 'High', 38))
        self.assertEqual(self.c.get('/api/admin/overview').status_code, 403)

    def test_last_address_is_only_the_customers_own(self):
        Order.objects.filter(id='ORD-1').update(shippingAddress={'addressLine': '12 Hill Rd', 'city': 'Mumbai', 'pinCode': '400001', 'fullName': 'Cathy'})
        self.assertEqual(self.c.get('/api/support/last-address').json()['address']['addressLine'], '12 Hill Rd')
        self.assertIsNone(self.a.get('/api/support/last-address').json()['address'])
        self.assertEqual(self.guest.get('/api/support/last-address').status_code, 401)


class AdminSellerReviewTests(RoleViewTests):
    def test_cannot_approve_without_aadhaar_pan_and_location(self):
        SellerApplication.objects.create(id='app-x', applicantName='Xena', companyName='Xena Mart', email='x@example.com', phone='9820000001', status='PENDING_ADMIN_APPROVAL')
        r = self.boss.post('/api/admin/seller-applications/app-x/action', {'action': 'APPROVE'}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('Aadhaar', r.json()['detail'])
        self.assertIn('PAN', r.json()['detail'])
        self.assertIn('location', r.json()['detail'])
        self.assertEqual(SellerApplication.objects.get(id='app-x').status, 'PENDING_ADMIN_APPROVAL')

    def test_admin_seller_detail_has_live_numbers_and_is_admin_only(self):
        from api.models import Seller
        Seller.objects.create(id='sel-1', name='Sita', companyName='Sita Stores', status='Approved')
        d = self.boss.get('/api/admin/sellers/sel-1/detail').json()
        self.assertEqual((d['live']['products'], d['live']['orders'], d['live']['revenue'], d['live']['lowStock']), (2, 1, 1000, 1))
        self.assertEqual(d['seller']['companyName'], 'Sita Stores')
        self.assertEqual(self.a.get('/api/admin/sellers/sel-1/detail').status_code, 403)  # a seller cannot see this
        self.assertEqual(self.c.get('/api/admin/sellers/sel-1/detail').status_code, 403)
        self.assertEqual(self.boss.get('/api/admin/sellers/nope/detail').status_code, 404)


class OnlyCustomersBuyTests(RoleViewTests):
    def order(self, client):
        return client.post('/api/orders', {'items': [{'id': 'a2', 'quantity': 1}], 'paymentMethod': 'Cash on Delivery',
                                           'shippingAddress': {'fullName': 'X', 'phone': '9820012345', 'addressLine': '1 Road', 'city': 'Mumbai', 'pinCode': '400001'}}, format='json')

    def test_only_customers_can_place_orders(self):
        self.assertEqual(self.guest.post('/api/orders', {}, format='json').status_code, 401)
        self.assertEqual(self.a.post('/api/orders', {'items': [{'id': 'a2', 'quantity': 1}]}, format='json').status_code, 403)  # a seller
        self.assertEqual(self.boss.post('/api/orders', {'items': [{'id': 'a2', 'quantity': 1}]}, format='json').status_code, 403)  # an admin
        self.assertIn('Only customer', self.a.post('/api/orders', {}, format='json').json()['detail'])
        self.assertEqual(Product.objects.get(id='a2').stock, 50)  # nothing was taken from stock
        self.assertEqual(self.order(self.c).status_code, 201)
        self.assertEqual(Product.objects.get(id='a2').stock, 49)


class SellerPhotosAndStockTests(RoleViewTests):
    def png(self, name='p.png'):
        import io
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        buf = io.BytesIO()
        Image.new('RGB', (40, 30), 'orange').save(buf, 'PNG')
        return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')

    def test_seller_adds_a_product_with_a_photo_and_it_is_served(self):
        import tempfile
        from pathlib import Path
        from unittest import mock
        from api import product_images
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(product_images, 'DIR', Path(tmp)):
            r = self.a.post('/api/seller/products', {'name': 'Steel Tiffin', 'category': 'Home & Kitchen', 'price': '350', 'stock': '12', 'image': self.png()}, format='multipart')
            self.assertEqual(r.status_code, 201)
            p = Product.objects.get(id=r.json()['id'])
            self.assertTrue(p.images[0].startswith('http') and '/api/media/product_images/' in p.images[0])
            self.assertEqual(APIClient().get(p.images[0].split('testserver')[-1]).status_code, 200)  # public, so customers can see it

    def test_a_non_image_is_refused(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        bad = SimpleUploadedFile('x.png', b'not really a picture', content_type='image/png')
        r = self.a.post('/api/seller/products', {'name': 'Steel Tiffin', 'category': 'Home', 'price': '350', 'stock': '12', 'image': bad}, format='multipart')
        self.assertEqual(r.status_code, 400)
        self.assertIn('not a picture', r.json()['detail'])
        self.assertFalse(Product.objects.filter(name='Steel Tiffin').exists())

    def test_manual_stock_edit_is_logged_and_only_for_own_products(self):
        self.assertEqual(self.a.patch('/api/seller/products/a2', {'stock': 80}, format='json').status_code, 200)
        h = self.a.get('/api/seller/products/a2/stock-log').json()['history']
        self.assertEqual((h[0]['change'], h[0]['reason'], h[0]['stockAfter']), (30, 'manual', 80))
        self.assertEqual(self.a.patch('/api/seller/products/b1', {'stock': 5}, format='json').status_code, 404)  # Ravi's product
        self.assertEqual(self.b.get('/api/seller/products/a2/stock-log').status_code, 404)

    def test_auto_restock_rule_tops_up_after_a_sale(self):
        self.a.patch('/api/seller/products/a1', {'autoRestock': True, 'reorderLevel': 3, 'restockQty': 25}, format='json')
        self.assertEqual(Product.objects.get(id='a1').stock, 3)  # a manual edit never triggers the rule; only a sale does
        Product.objects.filter(id='a2').update(stock=6, autoRestock=True, reorderLevel=5, restockQty=40)
        r = self.c.post('/api/orders', {'items': [{'id': 'a2', 'quantity': 2}], 'paymentMethod': 'Cash on Delivery',
                                       'shippingAddress': {'fullName': 'C', 'phone': '9820012345', 'addressLine': '1 Road', 'city': 'Mumbai', 'pinCode': '400001'}}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Product.objects.get(id='a2').stock, 6 - 2 + 40)  # sold 2, hit the level (4 <= 5), supplier top-up of 40 added
        reasons = [x['reason'] for x in self.a.get('/api/seller/products/a2/stock-log').json()['history']]
        self.assertEqual(reasons[:2], ['auto-restock', 'sale'])


class DamagedPhotoTests(RoleViewTests):
    def test_a_damaged_png_gets_a_friendly_error_not_a_server_error(self):
        import io
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        buf = io.BytesIO()
        Image.new('RGB', (60, 60), 'red').save(buf, 'PNG')
        broken = bytearray(buf.getvalue())
        broken[-20] ^= 0xFF  # corrupt the image data
        up = SimpleUploadedFile('p.png', bytes(broken), content_type='image/png')
        r = self.a.post('/api/seller/products', {'name': 'Steel Tiffin', 'category': 'Home', 'price': '350', 'stock': '3', 'image': up}, format='multipart')
        self.assertEqual(r.status_code, 400)
        self.assertIn('not a picture', r.json()['detail'])


class SellerSignupDraftTests(RoleViewTests):
    def test_creating_a_seller_account_opens_a_draft_the_admin_can_see(self):
        r = self.c.post('/api/seller/applications/start')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()['status'], 'DRAFT')
        again = self.c.post('/api/seller/applications/start')
        self.assertEqual((again.status_code, again.json()['id']), (200, r.json()['id']))  # no duplicates
        listed = self.boss.get('/api/seller/applications?status=DRAFT').json()
        self.assertEqual([a['applicantName'] for a in listed], ['Cathy Customer'])
        self.assertEqual(self.guest.post('/api/seller/applications/start').status_code, 401)
        self.assertEqual(self.c.get('/api/seller/applications').json()[0]['id'], r.json()['id'])  # and they can resume it


class ApprovalProfitAndChatLocationTests(RoleViewTests):
    def test_approval_turns_planned_products_into_listings_with_stock_and_photo(self):
        from api.models import SellerDocument
        app = SellerApplication.objects.create(
            id='app-new', applicantName='Nina', companyName='Nina Mart', email='n@example.com', phone='9820000000', status='PENDING_ADMIN_APPROVAL',
            storeLatitude=19.1, storeLongitude=72.8, city='Mumbai', productCategories=['Home & Kitchen'],
            plannedProducts=[{'name': 'Steel Tiffin', 'category': 'Home & Kitchen', 'approxPrice': 350, 'stock': 12, 'image': 'http://x/a.jpg'},
                             {'name': 'No Price Item', 'category': 'Home & Kitchen', 'approxPrice': 0, 'stock': 5}])
        for t in ('AADHAAR', 'PAN'):
            SellerDocument.objects.create(id=f'd-{t}', application=app, docType=t, fileName=t, mimeType='image/png')
        r = self.boss.post('/api/admin/seller-applications/app-new/action', {'action': 'APPROVE'}, format='json')
        self.assertEqual(r.status_code, 200)
        p = Product.objects.get(seller='Nina Mart', name='Steel Tiffin')
        self.assertEqual((p.stock, p.price, p.images), (12, 350, ['http://x/a.jpg']))
        self.assertFalse(Product.objects.filter(name='No Price Item').exists())  # a product with no price is not listed

    def test_profit_uses_cost_prices_and_asks_for_them_when_missing(self):
        before = self.a.post('/api/seller/assistant', {'message': 'What is my profit?'}, format='json').json()
        self.assertIn('cost', before['answer'].lower())
        self.a.patch('/api/seller/products/a1', {'costPrice': 300}, format='json')
        after = self.a.post('/api/seller/assistant', {'message': 'What is my profit?'}, format='json').json()
        self.assertIn('Profit so far', after['answer'])  # sold 2 x 500 = 1000, commission 60, cost 600 => 340
        self.assertIn('340', after['answer'])
        self.assertEqual(self.a.patch('/api/seller/products/a1', {'costPrice': -1}, format='json').status_code, 400)

    def test_chat_tells_the_customer_where_their_order_is(self):
        Order.objects.filter(id='ORD-1').update(shippingAddress={'addressLine': '12 Hill Rd', 'city': 'Mumbai', 'latitude': 19.07, 'longitude': 72.87})
        app = SellerApplication.objects.get(ownerUserId=self.s1.id)
        app.storeLatitude, app.storeLongitude, app.storeName = 19.12, 72.84, 'Sita Store'
        app.save()
        r = self.c.post('/api/support/chat', {'message': 'where is my order'}, format='json').json()
        self.assertIn('Sita Store', r['reply'])
        self.assertIn('km', r['reply'])
