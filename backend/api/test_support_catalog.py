"""Support chat, tickets and the public catalogue summary. The AI is switched off in tests."""

from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from api.models import Category, Product, SupportTicket, User
from api.views import generate_token


def authed(user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION='Bearer ' + generate_token(user))
    return c


class SupportTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(email='alice@example.com', name='Alice', password='pw-12345')
        self.bob = User.objects.create_user(email='bob@example.com', name='Bob', password='pw-12345')
        self.admin = User.objects.create_user(email='boss@example.com', name='Support Lead', password='pw-12345', role='ADMIN')
        self.a, self.b, self.boss, self.guest = authed(self.alice), authed(self.bob), authed(self.admin), APIClient()
        Product.objects.create(id='p1', name='Logitech Wireless Mouse', slug='logi-mouse', category='Electronics', brand='Logitech',
                               price=1195, originalPrice=1595, stock=20, rating=4.6, images=['x.jpg'])

    def test_chat_answers_from_the_catalogue_and_returns_cards(self):
        res = self.guest.post('/api/support/chat', {'message': 'wireless mouse under 1500'}, format='json').json()
        self.assertTrue(res['sessionId'])
        self.assertTrue(res['reply'])
        self.assertIn('Logitech Wireless Mouse', [c['name'] for c in res['cards']])
        self.assertIn('Talk to a person', res['suggestedActions'])

    def test_upset_customer_gets_an_urgent_ticket_with_the_chat_attached(self):
        first = self.a.post('/api/support/chat', {'message': 'where is my order'}, format='json').json()
        res = self.a.post('/api/support/chat', {'message': 'this is the worst service, I want to talk to a human',
                                                'sessionId': first['sessionId']}, format='json').json()
        self.assertTrue(res['escalated'])
        ticket = SupportTicket.objects.get(id=res['ticketId'])
        self.assertEqual(ticket.priority, 'URGENT')
        self.assertTrue(ticket.messages.filter(body__contains='where is my order').exists())

    def test_guest_cannot_open_a_ticket_by_chat(self):
        res = self.guest.post('/api/support/chat', {'message': 'I want to talk to a human'}, format='json').json()
        self.assertFalse(res['escalated'])
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_nobody_can_continue_someone_elses_chat(self):
        sid = self.a.post('/api/support/chat', {'message': 'hello'}, format='json').json()['sessionId']
        other = self.b.post('/api/support/chat', {'message': 'hi', 'sessionId': sid}, format='json').json()
        self.assertNotEqual(other['sessionId'], sid)

    def test_ticket_needs_consent_and_a_subject(self):
        body = {'subject': 'Damaged item', 'message': 'The box was crushed.', 'orderId': 'ord-2026-1234'}
        self.assertEqual(self.a.post('/api/support/tickets', body, format='json').status_code, 400)
        res = self.a.post('/api/support/tickets', {**body, 'consent': True}, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()['orderId'], 'ORD-2026-1234')
        self.assertEqual(self.a.post('/api/support/tickets', {'consent': True, 'message': 'x'}, format='json').status_code, 400)

    def test_customers_only_see_their_own_tickets(self):
        tid = self.a.post('/api/support/tickets', {'subject': 'Late', 'message': 'Order is late', 'consent': True}, format='json').json()['id']
        self.assertEqual(len(self.a.get('/api/support/tickets').json()), 1)
        self.assertEqual(self.b.get('/api/support/tickets').json(), [])
        self.assertEqual(self.b.get(f'/api/support/tickets/{tid}').status_code, 404)
        self.assertEqual(self.b.post(f'/api/support/tickets/{tid}/messages', {'body': 'hi'}, format='json').status_code, 404)
        self.assertEqual(self.guest.get('/api/support/tickets').status_code, 401)

    def test_support_team_can_reply_and_close(self):
        tid = self.a.post('/api/support/tickets', {'subject': 'Late', 'message': 'Order is late', 'consent': True}, format='json').json()['id']
        self.assertEqual(len(self.boss.get('/api/support/tickets').json()), 1)
        reply = self.boss.post(f'/api/support/tickets/{tid}/messages', {'body': 'We are checking with the store.'}, format='json').json()
        self.assertEqual(reply['status'], 'WAITING_CUSTOMER')
        self.assertEqual(self.a.patch(f'/api/support/tickets/{tid}', {'status': 'RESOLVED'}, format='json').status_code, 403)
        done = self.boss.patch(f'/api/support/tickets/{tid}', {'status': 'RESOLVED'}, format='json').json()
        self.assertEqual(done['status'], 'RESOLVED')

    def test_rating_is_saved_for_your_own_chat_only(self):
        sid = self.a.post('/api/support/chat', {'message': 'hello'}, format='json').json()['sessionId']
        self.assertEqual(self.b.post(f'/api/support/chat/{sid}/rating', {'rating': 5}, format='json').status_code, 404)
        self.assertEqual(self.a.post(f'/api/support/chat/{sid}/rating', {'rating': 9}, format='json').status_code, 400)
        self.assertEqual(self.a.post(f'/api/support/chat/{sid}/rating', {'rating': 5}, format='json').status_code, 200)
        self.assertEqual(self.boss.get('/api/support/summary').json()['averageRating'], 5.0)
        self.assertEqual(self.a.get('/api/support/summary').status_code, 403)


class CatalogSummaryTests(TestCase):
    def setUp(self):
        cache.clear()
        Category.objects.create(id='c1', name='Electronics', slug='electronics')
        Product.objects.create(id='p1', name='A', slug='a', category='Electronics', brand='Sony', price=100, rating=4.0, stock=5)
        Product.objects.create(id='p2', name='B', slug='b', category='Electronics', brand='Sony', price=900, rating=5.0, stock=0)

    def test_numbers_match_the_database_and_need_no_login(self):
        d = APIClient().get('/api/catalog/summary').json()
        self.assertEqual((d['totalProducts'], d['totalBrands'], d['inStock']), (2, 1, 1))
        self.assertEqual((d['priceMin'], d['priceMax'], d['averageRating']), (100, 900, 4.5))
        self.assertEqual(d['byCategory'], [{'name': 'Electronics', 'count': 2}])

    def test_ai_status_is_admin_only_and_never_shows_a_key(self):
        self.assertEqual(APIClient().get('/api/ai/status').status_code, 403)
        admin = User.objects.create_user(email='boss@example.com', name='Boss', password='pw-12345', role='ADMIN')
        res = authed(admin).get('/api/ai/status')
        self.assertEqual(res.status_code, 200)
        self.assertNotIn('key', ' '.join(res.json().keys()).lower().replace('configured', ''))
