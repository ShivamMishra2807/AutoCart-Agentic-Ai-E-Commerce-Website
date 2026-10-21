"""Reviews: who can write, what counts as a verified buyer, and what the public sees."""

from django.test import TestCase
from rest_framework.test import APIClient

from api.models import Order, Product, User
from api.views import generate_token


def authed(user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION='Bearer ' + generate_token(user))
    return c


class ReviewTests(TestCase):
    def setUp(self):
        self.anita = User.objects.create_user(email='anita@example.com', name='Anita Rao Menon', password='pw-12345')
        self.ben = User.objects.create_user(email='ben@example.com', name='Ben', password='pw-12345')
        self.a, self.b, self.guest = authed(self.anita), authed(self.ben), APIClient()
        Product.objects.create(id='p1', name='Mouse', slug='mouse', category='Electronics', price=500, stock=5)
        self.url = '/api/reviews/p1'
        self.body = {'rating': 5, 'title': 'Great', 'body': 'Works perfectly with my laptop and the battery lasts.'}

    def test_guest_can_read_but_not_write(self):
        self.assertEqual(self.guest.get(self.url).json()['count'], 0)
        self.assertEqual(self.guest.post(self.url, self.body, format='json').status_code, 401)

    def test_unknown_product_is_404(self):
        self.assertEqual(self.a.get('/api/reviews/nope').status_code, 404)

    def test_bad_review_gets_field_errors(self):
        res = self.a.post(self.url, {'rating': 9, 'body': 'short'}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(set(res.json()['errors']), {'rating', 'body'})

    def test_verified_only_after_a_real_purchase(self):
        self.assertFalse(self.a.post(self.url, self.body, format='json').json()['verified'])
        Order.objects.create(id='ORD-1', customerName='Anita', customerEmail='anita@example.com', items=[{'id': 'p1', 'quantity': 1}], status='Delivered')
        self.assertTrue(self.a.post(self.url, self.body, format='json').json()['verified'])  # the same review is updated and now verified
        Order.objects.create(id='ORD-2', customerName='Ben', customerEmail='ben@example.com', items=[{'id': 'p1', 'quantity': 1}], status='Cancelled')
        self.assertFalse(self.b.post(self.url, self.body, format='json').json()['verified'])  # a cancelled order does not count

    def test_one_review_per_person_and_it_can_be_edited(self):
        self.assertEqual(self.a.post(self.url, self.body, format='json').status_code, 201)
        res = self.a.post(self.url, {**self.body, 'rating': 3}, format='json')
        self.assertEqual(res.status_code, 200)
        data = self.guest.get(self.url).json()
        self.assertEqual((data['count'], data['average']), (1, 3.0))

    def test_summary_and_privacy(self):
        self.a.post(self.url, self.body, format='json')
        self.b.post(self.url, {**self.body, 'rating': 4}, format='json')
        data = self.guest.get(self.url).json()
        self.assertEqual((data['count'], data['average']), (2, 4.5))
        self.assertEqual((data['distribution']['5'], data['distribution']['4'], data['distribution']['1']), (1, 1, 0))
        names = {r['name'] for r in data['reviews']}
        self.assertEqual(names, {'Anita M.', 'Ben'})
        self.assertNotIn('example.com', str(data))
        self.assertIsNone(data['mine'])
        self.assertEqual(self.a.get(self.url).json()['mine']['rating'], 5)
