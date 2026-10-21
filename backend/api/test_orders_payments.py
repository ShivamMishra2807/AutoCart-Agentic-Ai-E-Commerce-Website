"""Orders and payments: the server decides prices and payment status, and orders stay private. No payment gateway is used."""

from django.test import TestCase
from rest_framework.test import APIClient

from api.models import Coupon, Order, Payment, Product, SellerApplication, Store, User
from api.views import generate_token


def authed(user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION='Bearer ' + generate_token(user))
    return c


class OrderTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(email='alice@example.com', name='Alice', password='pw-12345')
        self.bob = User.objects.create_user(email='bob@example.com', name='Bob', password='pw-12345')
        self.admin = User.objects.create_user(email='boss@example.com', name='Boss', password='pw-12345', role='ADMIN')
        self.a, self.b, self.boss, self.guest = authed(self.alice), authed(self.bob), authed(self.admin), APIClient()
        Product.objects.create(id='p1', name='Mouse', slug='mouse', category='Electronics', price=1000, stock=5, images=['m.jpg'])
        Product.objects.create(id='p2', name='Cable', slug='cable', category='Electronics', price=100, stock=2)
        Store.objects.create(id='s1', name='Andheri Store', address='x', city='Mumbai', pincode='400069', latitude=19.1, longitude=72.8)

    def place(self, client=None, items=None, **over):
        body = {'items': items or [{'id': 'p1', 'quantity': 2, 'price': 1}], 'paymentMethod': 'Cash on Delivery',
                'shippingAddress': {'fullName': 'Alice', 'phone': '9820012345', 'addressLine': 'x', 'city': 'Mumbai'}, **over}
        return (client or self.a).post('/api/orders', body, format='json')

    def test_guest_cannot_order(self):
        self.assertEqual(self.place(self.guest).status_code, 401)

    def test_prices_come_from_the_database_not_the_browser(self):
        res = self.place(items=[{'id': 'p1', 'quantity': 2, 'price': 1}], totalAmount=1, subtotal=1, userEmail='bob@example.com')
        self.assertEqual(res.status_code, 201, res.content)
        o = Order.objects.get(id=res.json()['id'])
        self.assertEqual((o.subtotal, o.shippingFee, o.totalAmount), (2000.0, 0.0, 2000.0))  # over 499: free delivery
        self.assertEqual(o.customerEmail, 'alice@example.com')  # not the email in the request
        self.assertEqual(o.items[0]['price'], 1000)

    def test_small_order_pays_the_delivery_fee(self):
        res = self.place(items=[{'id': 'p2', 'quantity': 1}])
        self.assertEqual(res.json()['totalAmount'], 140.0)

    def test_stock_goes_down_and_cannot_go_below_zero(self):
        self.assertEqual(self.place(items=[{'id': 'p1', 'quantity': 5}]).status_code, 201)
        p = Product.objects.get(id='p1')
        self.assertEqual((p.stock, p.stockStatus), (0, 'Out of Stock'))
        res = self.place(items=[{'id': 'p1', 'quantity': 1}])
        self.assertEqual(res.status_code, 409)
        self.assertIn('out of stock', res.json()['detail'].lower())
        self.assertEqual(Product.objects.get(id='p1').stock, 0)

    def test_asking_for_more_than_is_left_is_refused_and_changes_nothing(self):
        res = self.place(items=[{'id': 'p1', 'quantity': 3}, {'id': 'p2', 'quantity': 9}])
        self.assertEqual(res.status_code, 409)
        self.assertEqual((Product.objects.get(id='p1').stock, Product.objects.get(id='p2').stock), (5, 2))
        self.assertEqual(Order.objects.count(), 0)

    def test_payment_status_is_never_paid_by_default(self):
        cod = self.place(items=[{'id': 'p2', 'quantity': 1}]).json()
        self.assertEqual((cod['paymentStatus'], cod['status']), ('Pending', 'Confirmed'))
        pod = self.place(items=[{'id': 'p2', 'quantity': 1}], paymentMethod='UPI or Card on Delivery').json()
        self.assertEqual((pod['paymentStatus'], pod['status'], pod['paymentRequired']), ('Pending', 'Confirmed', False))
        self.assertEqual(self.place(paymentMethod='UPI').status_code, 400)  # unknown methods are refused
        self.assertEqual(self.place(paymentMethod='Razorpay (Test Mode)').status_code, 400)  # the gateway is gone

    def test_pay_at_store_needs_a_store(self):
        self.assertEqual(self.place(paymentMethod='Pay at Store').status_code, 400)
        ok = self.place(paymentMethod='Pay at Store', storeId='s1')
        self.assertEqual(ok.status_code, 201)
        self.assertEqual(ok.json()['shippingAddress']['storeName'], 'Andheri Store')

    def test_coupon_is_checked_on_the_server(self):
        Coupon.objects.create(id='c1', code='SAVE10', discountType='Percentage', discountValue=10, maxDiscount=150, minOrderAmount=500, status='Active')
        res = self.place(couponCode='save10')
        self.assertEqual((res.json()['discountAmount'], res.json()['totalAmount']), (150.0, 1850.0))
        self.assertEqual(self.place(items=[{'id': 'p2', 'quantity': 1}], couponCode='SAVE10').status_code, 400)  # below the minimum
        self.assertEqual(self.place(couponCode='NOPE').status_code, 400)

    def test_orders_are_private_to_their_owner(self):
        oid = self.place().json()['id']
        for path in (f'/api/orders/{oid}', f'/api/orders/{oid}/tracking'):
            self.assertEqual(self.guest.get(path).status_code, 401, path)
            self.assertEqual(self.b.get(path).status_code, 404, path)
            self.assertEqual(self.a.get(path).status_code, 200, path)
            self.assertEqual(self.boss.get(path).status_code, 200, path)
        self.assertEqual(self.b.post(f'/api/orders/{oid}/cancel').status_code, 404)
        self.assertEqual(self.guest.post(f'/api/orders/{oid}/cancel').status_code, 401)

    def test_cancelling_puts_the_stock_back(self):
        oid = self.place(items=[{'id': 'p1', 'quantity': 3}]).json()['id']
        self.assertEqual(Product.objects.get(id='p1').stock, 2)
        res = self.a.post(f'/api/orders/{oid}/cancel')
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(Product.objects.get(id='p1').stock, 5)
        self.assertEqual(Order.objects.get(id=oid).status, 'Cancelled')
        self.assertEqual(self.a.post(f'/api/orders/{oid}/cancel').status_code, 400)  # already cancelled

    def test_return_only_after_delivery(self):
        oid = self.place().json()['id']
        self.assertEqual(self.a.post(f'/api/orders/{oid}/return').status_code, 400)
        Order.objects.filter(id=oid).update(status='Delivered')
        self.assertEqual(self.a.post(f'/api/orders/{oid}/return').status_code, 200)


class UpiScanAndPayTests(TestCase):
    """Customer pays the seller's own UPI ID; the seller confirms the money arrived."""

    def setUp(self):
        self.cust = User.objects.create_user(email='c@example.com', name='Cathy', password='pw-12345')
        self.other = User.objects.create_user(email='o@example.com', name='Omar', password='pw-12345')
        self.seller = User.objects.create_user(email='s@example.com', name='Sita', password='pw-12345', role='SELLER')
        self.rival = User.objects.create_user(email='r@example.com', name='Ravi', password='pw-12345', role='SELLER')
        self.admin = User.objects.create_user(email='a@example.com', name='Boss', password='pw-12345', role='ADMIN')
        SellerApplication.objects.create(id='app-s', ownerUserId=self.seller.id, applicantName='Sita', companyName='Sita Stores', email='s@example.com', phone='9820012345', status='APPROVED')
        SellerApplication.objects.create(id='app-r', ownerUserId=self.rival.id, applicantName='Ravi', companyName='Ravi Mart', email='r@example.com', phone='9820012346', status='APPROVED')
        Product.objects.create(id='p1', name='Flask', slug='flask', category='Home', price=500, stock=10, seller='Sita Stores')
        Product.objects.create(id='p2', name='Lamp', slug='lamp', category='Home', price=900, stock=10, seller='Ravi Mart')
        self.c, self.o, self.s, self.r, self.boss, self.guest = authed(self.cust), authed(self.other), authed(self.seller), authed(self.rival), authed(self.admin), APIClient()

    def order(self, items=None):
        return self.c.post('/api/orders', {'items': items or [{'id': 'p1', 'quantity': 1}], 'paymentMethod': 'UPI (Scan & Pay)',
                                           'shippingAddress': {'fullName': 'Cathy', 'phone': '9820012345', 'addressLine': '1 Road', 'city': 'Mumbai'}}, format='json')

    def test_upi_needs_a_seller_upi_id_and_a_single_seller(self):
        r = self.order()
        self.assertEqual(r.status_code, 400)  # Sita has not added a UPI ID
        self.assertIn('UPI ID', r.json()['detail'])
        self.assertEqual(Order.objects.count(), 0)
        self.s.put('/api/seller/payout-settings', {'upiId': 'sita@okaxis'}, format='json')
        mixed = self.order([{'id': 'p1', 'quantity': 1}, {'id': 'p2', 'quantity': 1}])
        self.assertEqual(mixed.status_code, 400)
        self.assertIn('one seller', mixed.json()['detail'])
        self.assertEqual(Product.objects.get(id='p1').stock, 10)  # nothing was taken

    def test_bad_upi_id_is_refused_and_buyers_cannot_set_one(self):
        self.assertEqual(self.s.put('/api/seller/payout-settings', {'upiId': 'not valid'}, format='json').status_code, 400)
        self.assertEqual(self.c.put('/api/seller/payout-settings', {'upiId': 'x@okaxis'}, format='json').status_code, 403)

    def test_full_flow_pay_submit_reference_seller_confirms(self):
        self.s.put('/api/seller/payout-settings', {'upiId': 'sita@okaxis'}, format='json')
        o = self.order().json()
        self.assertEqual((o['paymentStatus'], o['status'], o['paymentRequired']), ('Awaiting Payment', 'Pending', True))
        self.assertIn('pa=sita%40okaxis', o['upi']['link'])
        oid = o['id']
        self.assertEqual(self.o.get(f'/api/orders/{oid}/upi').status_code, 404)  # someone else's order
        self.assertEqual(self.c.get(f'/api/orders/{oid}/upi').json()['amount'], o['totalAmount'])
        self.assertEqual(self.s.post(f'/api/orders/{oid}/payment', {'action': 'received'}, format='json').status_code, 400)  # nothing submitted yet
        self.assertEqual(self.c.post(f'/api/orders/{oid}/upi-reference', {'utr': '12345'}, format='json').status_code, 400)
        self.assertEqual(self.c.post(f'/api/orders/{oid}/upi-reference', {'utr': '123456789012'}, format='json').json()['paymentStatus'], 'Verifying')
        self.assertEqual(self.c.post(f'/api/orders/{oid}/payment', {'action': 'received'}, format='json').status_code, 403)  # the buyer cannot confirm their own payment
        self.assertEqual(self.r.post(f'/api/orders/{oid}/payment', {'action': 'received'}, format='json').status_code, 403)  # a different seller cannot
        done = self.s.post(f'/api/orders/{oid}/payment', {'action': 'received'}, format='json').json()
        self.assertEqual((done['paymentStatus'], done['status']), ('Paid', 'Confirmed'))

    def test_reference_cannot_be_reused_and_a_rejected_payment_can_be_retried(self):
        self.s.put('/api/seller/payout-settings', {'upiId': 'sita@okaxis'}, format='json')
        one, two = self.order().json()['id'], self.order().json()['id']
        self.c.post(f'/api/orders/{one}/upi-reference', {'utr': '123456789012'}, format='json')
        self.assertEqual(self.c.post(f'/api/orders/{two}/upi-reference', {'utr': '123456789012'}, format='json').status_code, 409)
        self.s.post(f'/api/orders/{one}/payment', {'action': 'not_received'}, format='json')
        self.assertEqual(Order.objects.get(id=one).paymentStatus, 'Failed')
        self.assertEqual(self.c.post(f'/api/orders/{one}/upi-reference', {'utr': '999999999999'}, format='json').status_code, 200)  # try again with the right number

    def test_seller_cannot_pack_until_paid_and_admin_sees_waiting_payments(self):
        self.s.put('/api/seller/payout-settings', {'upiId': 'sita@okaxis'}, format='json')
        oid = self.order().json()['id']
        self.assertEqual(self.s.post(f'/api/seller/orders/{oid}/pack').status_code, 400)
        self.c.post(f'/api/orders/{oid}/upi-reference', {'utr': '123456789012'}, format='json')
        waiting = self.boss.get('/api/payments/status').json()['waiting']
        self.assertEqual((waiting[0]['orderId'], waiting[0]['utr'], waiting[0]['seller']), (oid, '123456789012', 'Sita Stores'))
        self.assertEqual(self.c.get('/api/payments/status').status_code, 403)
        self.s.post(f'/api/orders/{oid}/payment', {'action': 'received'}, format='json')
        self.assertEqual(self.s.post(f'/api/seller/orders/{oid}/pack').json()['status'], 'Packed')

    def test_checkout_knows_when_upi_cannot_work(self):
        c = APIClient()
        empty = c.post('/api/payments/upi-check', {'items': []}, format='json').json()
        self.assertEqual(empty['available'], False)
        no_upi = c.post('/api/payments/upi-check', {'items': [{'id': 'p1'}]}, format='json').json()
        self.assertEqual(no_upi['available'], False)
        self.assertIn('UPI ID', no_upi['reason'])
        self.s.put('/api/seller/payout-settings', {'upiId': 'sita@okaxis'}, format='json')
        yes = c.post('/api/payments/upi-check', {'items': [{'id': 'p1'}]}, format='json').json()
        self.assertEqual((yes['available'], yes['payee']), (True, 'Sita Stores'))
        mixed = c.post('/api/payments/upi-check', {'items': [{'id': 'p1'}, {'id': 'p2'}]}, format='json').json()
        self.assertEqual(mixed['available'], False)
