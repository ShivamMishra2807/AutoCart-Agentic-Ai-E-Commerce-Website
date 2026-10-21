"""Customer enquiries: who can ask, who can answer, and what the public sees."""

from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from api.models import Enquiry, Product, SellerApplication, User
from api.views import generate_token


def authed(user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION='Bearer ' + generate_token(user))
    return c


class EnquiryTests(TestCase):
    def setUp(self):
        cache.clear()  # the form is rate limited per address
        self.seller_user = User.objects.create_user(email='seller@example.com', name='Sita Seller', password='pw-12345', role='SELLER')
        self.rival_user = User.objects.create_user(email='rival@example.com', name='Rival Seller', password='pw-12345', role='SELLER')
        self.customer = User.objects.create_user(email='anita@example.com', name='Anita Rao', password='pw-12345')
        self.admin = User.objects.create_user(email='boss@example.com', name='Boss', password='pw-12345', role='ADMIN')
        for owner, name in ((self.seller_user, 'Sita Stores'), (self.rival_user, 'Rival Mart')):
            SellerApplication.objects.create(id=f'app-{owner.id}', ownerUserId=owner.id, applicantName=owner.name, companyName=name,
                                             email=owner.email, phone='9820012345', city='Mumbai', status='APPROVED')
        Product.objects.create(id='p1', name='Steel Flask', slug='steel-flask', category='Home', seller='Sita Stores', price=500, stock=5)
        self.guest, self.cust, self.sel, self.rival, self.boss = APIClient(), authed(self.customer), authed(self.seller_user), authed(self.rival_user), authed(self.admin)

    def ask(self, client=None, **over):
        body = {'productId': 'p1', 'message': 'Does this flask keep water cold for 24 hours?', 'name': 'Guest Person', 'email': 'guest@example.com', **over}
        return (client or self.guest).post('/api/enquiries', body, format='json')

    def test_guest_can_ask_with_name_and_email(self):
        res = self.ask()
        self.assertEqual(res.status_code, 201)
        e = Enquiry.objects.get(id=res.json()['id'])
        self.assertEqual((e.productName, e.sellerName), ('Steel Flask', 'Sita Stores'))

    def test_bad_enquiry_gets_field_errors(self):
        res = self.ask(message='hi', email='nope')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(set(res.json()['errors']), {'message', 'email'})

    def test_signed_in_customer_needs_no_name_or_email(self):
        res = self.cust.post('/api/enquiries', {'message': 'Is the store open on Sundays?'}, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()['customerEmail'], 'anita@example.com')

    def test_only_the_right_seller_or_admin_can_answer(self):
        eid = self.ask().json()['id']
        url = f'/api/enquiries/{eid}/answer'
        self.assertEqual(self.guest.post(url, {'answer': 'x'}, format='json').status_code, 401)
        self.assertEqual(self.cust.post(url, {'answer': 'x'}, format='json').status_code, 404)
        self.assertEqual(self.rival.post(url, {'answer': 'x'}, format='json').status_code, 404)
        self.assertEqual(self.sel.post(url, {'answer': ''}, format='json').status_code, 400)
        self.assertEqual(self.sel.post(url, {'answer': 'Yes, it stays cold for 24 hours.'}, format='json').status_code, 200)

    def test_seller_sees_only_their_products_questions(self):
        self.ask()
        self.assertEqual(len(self.sel.get('/api/enquiries').json()), 1)
        self.assertEqual(self.rival.get('/api/enquiries').json(), [])
        self.assertEqual(len(self.boss.get('/api/enquiries').json()), 1)
        self.assertEqual(self.guest.get('/api/enquiries').status_code, 401)

    def test_customer_sees_their_own_enquiries_and_the_answer(self):
        self.cust.post('/api/enquiries', {'productId': 'p1', 'message': 'Is this dishwasher safe please?'}, format='json')
        eid = self.cust.get('/api/enquiries').json()[0]['id']
        self.sel.post(f'/api/enquiries/{eid}/answer', {'answer': 'Hand wash only.'}, format='json')
        mine = self.cust.get('/api/enquiries').json()
        self.assertEqual((mine[0]['status'], mine[0]['answer']), ('ANSWERED', 'Hand wash only.'))

    def test_public_answer_shows_first_name_only_and_no_contact_details(self):
        eid = self.ask(name='Priya Venkataraman', email='priya@secret.example', phone='9999999999').json()['id']
        self.assertEqual(self.guest.get('/api/product-questions/p1').json(), [])  # unanswered: not public
        self.sel.post(f'/api/enquiries/{eid}/answer', {'answer': 'Yes, 24 hours.', 'isPublic': True}, format='json')
        shown = self.guest.get('/api/product-questions/p1').json()
        self.assertEqual(shown[0]['asker'], 'Priya')
        self.assertNotIn('secret.example', str(shown))
        self.assertNotIn('9999999999', str(shown))

    def test_private_answer_stays_off_the_product_page(self):
        eid = self.ask().json()['id']
        self.sel.post(f'/api/enquiries/{eid}/answer', {'answer': 'Please call the store.', 'isPublic': False}, format='json')
        self.assertEqual(self.guest.get('/api/product-questions/p1').json(), [])

    def test_general_enquiry_is_answered_by_admin_and_never_public(self):
        eid = self.guest.post('/api/enquiries', {'message': 'Do you deliver to Thane?', 'name': 'Raj', 'email': 'raj@example.com'}, format='json').json()['id']
        self.assertEqual(self.sel.post(f'/api/enquiries/{eid}/answer', {'answer': 'x'}, format='json').status_code, 404)
        self.assertEqual(self.boss.post(f'/api/enquiries/{eid}/answer', {'answer': 'Yes, we do.', 'isPublic': True}, format='json').status_code, 200)
        self.assertFalse(Enquiry.objects.get(id=eid).isPublic)
