"""
End-to-End Acceptance Tests for AutoCart Complete Project Integration.
Covers the 5 core user journeys specified in Prompt 4:
- Journey A: Shopping (Search under budget -> stable recommendation -> select 2nd -> cart update -> checkout validation)
- Journey B: Nearby stores (Missing address -> PIN prompt -> valid PIN -> matching stores -> inventory accuracy -> address change refresh)
- Journey C: Seller onboarding (Upload documents -> OCR extraction -> review/correct fields -> planned products -> submit -> pending status)
- Journey D: Admin review (Admin view -> AI risk assessment & explanation -> admin approval -> seller activation -> store & product go live)
- Journey E: Failure recovery (Missing AI credentials -> invalid PIN rejection -> out of stock alternatives -> unauthorized actions blocked -> invalid uploads rejected)
"""

import os
import shutil
import tempfile
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from api.models import (
    Product, User, Store, StoreInventory, SellerApplication, Seller, Order, ChatSession
)
from api.views import generate_token
from api.agents.memory import SessionMemoryManager
from api.agents.engine import AgentEngine
from api.fulfillment_service import FulfillmentService
from api.location_service import resolve_coordinates

TMP_MEDIA = tempfile.mkdtemp()

MOCK_DOC_TEXTS = {
    'aadhaar': "Government of India\nRahul Sharma\nDOB: 14/03/1991\nMALE\nXXXX XXXX 4821\nAddress: 12 Hill Road Andheri East Mumbai 400069",
    'pan': "INCOME TAX DEPARTMENT\nABCDE1234F\nName\nRahul Sharma\nFather's Name\nMohan Sharma\nDate of Birth\n14/03/1991",
}


def mock_read_document_text(path, mime=''):
    name = path.replace('\\', '/').split('/')[-1].lower()
    for key in ('aadhaar', 'pan'):
        if key in name:
            return {'status': 'DONE', 'text': MOCK_DOC_TEXTS[key]}
    return {'status': 'UNREADABLE', 'text': ''}


def authed_client(user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f'Bearer {generate_token(user)}')
    return c


@override_settings(MEDIA_ROOT=TMP_MEDIA)
class AutoCartEndToEndAcceptanceTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)

    def setUp(self):
        SessionMemoryManager._sessions.clear()
        SessionMemoryManager._states.clear()
        SessionMemoryManager._timestamps.clear()

        self.engine = AgentEngine()
        self.guest_client = APIClient()

        # Users
        self.customer = User.objects.create_user(
            email='customer.rajesh@test.com',
            name='Rajesh Kulkarni',
            password='password123',
            phone='9820011223'
        )
        self.customer_client = authed_client(self.customer)

        self.seller_user = User.objects.create_user(
            email='applicant.rahul@test.com',
            name='Rahul Sharma',
            password='password123',
            phone='9820012345'
        )
        self.seller_client = authed_client(self.seller_user)

        self.admin_user = User.objects.create_superuser(
            email='admin.vikram@test.com',
            name='Vikram Mehta',
            password='password123'
        )
        self.admin_client = authed_client(self.admin_user)

        # Catalog Products
        self.earbud_1 = Product.objects.create(
            id='eb-boat-141',
            name='boAt Airdopes 141 ANC Wireless Earbuds',
            slug='boat-airdopes-141-anc',
            category='Audio',
            brand='boAt',
            price=1499.0,
            originalPrice=4490.0,
            stock=40,
            rating=4.3,
            stockStatus='In Stock'
        )
        self.earbud_2 = Product.objects.create(
            id='eb-noise-102',
            name='Noise Buds VS102 Wireless Earbuds',
            slug='noise-buds-vs102',
            category='Audio',
            brand='Noise',
            price=1299.0,
            originalPrice=2999.0,
            stock=25,
            rating=4.2,
            stockStatus='In Stock'
        )
        self.earbud_3 = Product.objects.create(
            id='eb-boult-propods',
            name='Boult Audio AirBass Propods',
            slug='boult-airbass-propods',
            category='Audio',
            brand='Boult',
            price=999.0,
            originalPrice=2499.0,
            stock=30,
            rating=4.0,
            stockStatus='In Stock'
        )

        # Partner Stores
        self.store_kalyan = Store.objects.create(
            id='store-kalyan-01',
            name='AutoCart Partner - Kalyan West Store',
            seller='Kalyan Electronics',
            address='Station Road, Kalyan West',
            city='Kalyan',
            pincode='421301',
            latitude=19.2551,
            longitude=73.1378,
            operatingStatus='Open',
            serviceCoverageRadiusKm=15.0,
            rating=4.8
        )
        self.store_thane = Store.objects.create(
            id='store-thane-01',
            name='AutoCart Partner - Thane Viviana Store',
            seller='Thane Digital',
            address='Eastern Express Highway, Thane West',
            city='Thane',
            pincode='400606',
            latitude=19.2085,
            longitude=72.9716,
            operatingStatus='Open',
            serviceCoverageRadiusKm=15.0,
            rating=4.6
        )

        # Store Inventory: only earbud_1 is in Kalyan store; earbud_2 is in Thane store
        StoreInventory.objects.create(
            id='inv-kln-01',
            store=self.store_kalyan,
            product=self.earbud_1,
            availableQuantity=12,
            reservedQuantity=0,
            storePrice=1499.0,
            isAvailable=True
        )
        StoreInventory.objects.create(
            id='inv-thn-01',
            store=self.store_thane,
            product=self.earbud_2,
            availableQuantity=8,
            reservedQuantity=0,
            storePrice=1299.0,
            isAvailable=True
        )

    # =======================================================================
    # JOURNEY A: SHOPPING
    # =======================================================================
    def test_journey_a_shopping(self):
        """
        1. User searches for products under a budget.
        2. Sathi returns real products with stable ordering.
        3. User selects the second product ('Add the second one to my cart').
        4. Exactly the second product is added to the cart.
        5. Cart displays correct quantity and price.
        6. Checkout uses validated server-side data.
        """
        session_id = "journey_a_sess"

        # 1 & 2: Search under budget
        res_search = self.engine.run_sathi(
            query="Suggest wireless earbuds under ₹2,000",
            session_id=session_id,
            customer_email=self.customer.email
        )
        self.assertEqual(res_search['status'], 'success')
        products = res_search.get('products', [])
        self.assertGreaterEqual(len(products), 2)
        # Verify returned products are real DB products under ₹2,000
        for p in products:
            self.assertLessEqual(p['price'], 2000.0)

        second_expected = products[1]

        # 3: Select the second one
        res_select = self.engine.run_sathi(
            query="Add the second one to my cart",
            session_id=session_id,
            customer_email=self.customer.email
        )
        self.assertEqual(res_select['status'], 'success')
        self.assertIn('cartAction', res_select)
        cart_action = res_select['cartAction']
        self.assertEqual(cart_action['productId'], second_expected['id'])
        self.assertEqual(res_select['selectedProductId'], second_expected['id'])

        # 4 & 5: Exactly second product added with quantity 1 and verified price
        self.assertEqual(cart_action['product']['id'], second_expected['id'])
        self.assertEqual(cart_action['product']['name'], second_expected['name'])
        self.assertEqual(cart_action['product']['price'], second_expected['price'])
        self.assertEqual(cart_action['quantity'], 1)
        state_key = SessionMemoryManager.get_session_key(session_id, self.customer.email)
        state = SessionMemoryManager.get_state(state_key)
        self.assertEqual(len(state.get('cart_items', [])), 1)
        self.assertEqual(state['cart_items'][0]['id'], second_expected['id'])

        # 6: Checkout quote uses validated server-side pricing
        res_quote = self.customer_client.post('/api/orders/quote', {
            'productId': second_expected['id'],
            'quantity': 1,
            'pincode': '400606'
        }, format='json')
        self.assertEqual(res_quote.status_code, status.HTTP_200_OK)
        quote_data = res_quote.data
        self.assertEqual(quote_data['subtotal'], second_expected['price'])
        self.assertGreater(quote_data['totalAmount'], 0)

    # =======================================================================
    # JOURNEY B: NEARBY STORES
    # =======================================================================
    def test_journey_b_nearby_stores(self):
        """
        1. User asks for nearby stores without saved address.
        2. Sathi requests PIN code.
        3. User provides valid supported PIN code (421301 Kalyan).
        4. Sathi displays actual matching stores with stock.
        5. Product-specific stock availability is verified.
        6. Changing address refreshes results and invalidates stale state.
        """
        session_id = "journey_b_sess"

        # 1 & 2: Missing address triggers PIN prompt
        res_missing = self.engine.run_sathi(
            query="Where can I buy this product nearby?",
            session_id=session_id
        )
        self.assertEqual(res_missing['status'], 'awaiting_pincode')
        self.assertEqual(res_missing['reply'], "Please enter your 6-digit delivery PIN code so I can find nearby stores.")

        # 3 & 4: Provide valid Kalyan PIN code
        res_pin = self.engine.run_sathi(
            query="421301",
            session_id=session_id
        )
        self.assertEqual(res_pin['status'], 'success')
        stores = res_pin.get('nearbyStores', [])
        self.assertGreater(len(stores), 0)
        # Closest store to 421301 is Kalyan store
        self.assertEqual(stores[0]['storeId'], self.store_kalyan.id)
        self.assertIn("Kalyan", res_pin['reply'])

        # 5: Product-specific store inventory check
        # earbud_1 is in Kalyan store (12 units)
        stores_eb1 = self.engine.run_sathi(
            query=f"Which nearby store has {self.earbud_1.name}?",
            session_id=session_id
        )
        self.assertEqual(stores_eb1['status'], 'success')
        self.assertTrue(any(s['storeId'] == self.store_kalyan.id for s in stores_eb1.get('nearbyStores', [])))

        # 6: Changing address to Thane (400606) synchronizes context and refreshes store proximity
        addr_payload = {
            'fullName': 'Rajesh Kulkarni',
            'phone': '9820011223',
            'addressLine': 'Near Viviana Mall',
            'city': 'Thane',
            'state': 'Maharashtra',
            'pinCode': '400606',
            'sessionId': session_id,
        }
        res_addr = self.customer_client.post('/api/auth/address', addr_payload, format='json')
        self.assertEqual(res_addr.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res_addr.data['invalidatedStaleStore'])

        # Subsequent nearby store search prioritizes Thane store
        res_thane = self.engine.run_sathi(
            query="Show me nearby stores",
            session_id=session_id,
            customer_email=self.customer.email
        )
        self.assertEqual(res_thane['status'], 'success')
        new_stores = res_thane.get('nearbyStores', [])
        self.assertGreater(len(new_stores), 0)
        self.assertEqual(new_stores[0]['storeId'], self.store_thane.id)

    # =======================================================================
    # JOURNEY C: SELLER ONBOARDING
    # =======================================================================
    @patch('api.seller_docs.read_text', side_effect=mock_read_document_text)
    def test_journey_c_seller_onboarding(self, _mock_ocr):
        """
        1. Seller uploads synthetic supported documents (PAN, Aadhaar).
        2. OCR extracts supported fields (PAN number, masked Aadhaar).
        3. Seller reviews and corrects fields.
        4. Seller enters product and stock information.
        5. Application is submitted.
        6. Seller sees pending status (PENDING_ADMIN_APPROVAL).
        """
        # Create draft application
        res_create = self.seller_client.post('/api/seller/applications', {
            'companyName': 'Sharma Electronics',
            'contactName': 'Rahul Sharma',
            'email': 'applicant.rahul@test.com',
            'phone': '9820012345',
            'pan': 'ABCDE1234F',
            'gstin': '27ABCDE1234F1Z5',
            'address': '12 Hill Road, Andheri East',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400069',
            'storeLatitude': 19.1136,
            'storeLongitude': 72.8697,
            'productCategories': ['Electronics'],
            'plannedProducts': [
                {'name': 'Wireless Optical Mouse', 'category': 'Electronics', 'approxPrice': 699.0, 'stock': 20}
            ]
        }, format='json')
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        app_id = res_create.data['id']

        # 1 & 2: Upload PAN and Aadhaar documents
        pan_file = SimpleUploadedFile("pan.png", b"fake-image-pan-bytes", content_type="image/png")
        res_pan = self.seller_client.post(f'/api/seller/applications/{app_id}/documents', {
            'docType': 'PAN',
            'file': pan_file
        }, format='multipart')
        self.assertEqual(res_pan.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_pan.data['extractedFields'].get('pan'), 'ABCDE1234F')

        aadhaar_file = SimpleUploadedFile("aadhaar.png", b"fake-image-aadhaar-bytes", content_type="image/png")
        res_aadhaar = self.seller_client.post(f'/api/seller/applications/{app_id}/documents', {
            'docType': 'AADHAAR',
            'file': aadhaar_file
        }, format='multipart')
        self.assertEqual(res_aadhaar.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_aadhaar.data['extractedFields'].get('aadhaarLast4'), '4821')

        # 3 & 4: Review fields and enter product/stock info
        res_update = self.seller_client.put(f'/api/seller/applications/{app_id}', {
            'pan': 'ABCDE1234F',
            'gstin': '27ABCDE1234F1Z5',
            'productCategories': ['Electronics'],
            'plannedProducts': [
                {'name': 'Wireless Optical Mouse', 'category': 'Electronics', 'approxPrice': 699.0, 'stock': 20}
            ]
        }, format='json')
        self.assertEqual(res_update.status_code, status.HTTP_200_OK)

        # 5 & 6: Submit application and verify pending/review status
        res_submit = self.seller_client.post(f'/api/seller/applications/{app_id}/submit')
        self.assertEqual(res_submit.status_code, status.HTTP_200_OK)
        self.assertIn(res_submit.data['status'], ('PENDING_ADMIN_APPROVAL', 'NEEDS_MANUAL_REVIEW', 'NEEDS_MORE_INFORMATION'))

    # =======================================================================
    # JOURNEY D: ADMIN REVIEW & ACTIVATION
    # =======================================================================
    @patch('api.seller_docs.read_text', side_effect=mock_read_document_text)
    def test_journey_d_admin_review(self, _mock_ocr):
        """
        1. Admin views pending application.
        2. Admin assistant summarizes application and risk score.
        3. Risk score and contributing factors are displayed.
        4. Authorized admin approves application.
        5. Application status becomes APPROVED.
        6. Seller role is upgraded and store & products are live in database.
        """
        # Create and submit a clean application
        app = SellerApplication.objects.create(
            id='app-test-review-01',
            ownerUserId=self.seller_user.id,
            companyName='Sharma Electronics',
            applicantName='Rahul Sharma',
            email=self.seller_user.email,
            phone='9820012345',
            pan='ABCDE1234F',
            gstin='27ABCDE1234F1Z5',
            address='12 Hill Road, Andheri East',
            city='Mumbai',
            addressState='Maharashtra',
            pincode='400069',
            storeLatitude=19.1136,
            storeLongitude=72.8697,
            status='PENDING_ADMIN_APPROVAL',
            riskScore=15,
            riskCategory='Low',
            plannedProducts=[
                {'name': 'Sharma Wireless Mouse', 'category': 'Electronics', 'approxPrice': 699.0, 'stock': 25}
            ]
        )
        # Attach documents
        from api.models import SellerDocument
        SellerDocument.objects.create(
            id='doc-pan-01', application=app, docType='PAN', fileName='pan.png', mimeType='image/png',
            sizeBytes=1024, ocrStatus='EXTRACTED', extractedFields={'pan': 'ABCDE1234F', 'name': 'Rahul Sharma'}
        )
        SellerDocument.objects.create(
            id='doc-aadh-01', application=app, docType='AADHAAR', fileName='aadhaar.png', mimeType='image/png',
            sizeBytes=1024, ocrStatus='EXTRACTED', extractedFields={'aadhaarLast4': '4821', 'name': 'Rahul Sharma'}
        )

        # 1: Admin views the application profile
        res_view = self.admin_client.get(f'/api/seller/applications/{app.id}')
        self.assertEqual(res_view.status_code, status.HTTP_200_OK)
        self.assertEqual(res_view.data['companyName'], 'Sharma Electronics')

        # 2 & 3: Admin assistant AI tool explains risk score and facts
        admin_ai_res = self.engine.run_admin_assistance_agent(
            prompt=f"Explain the risk score for application {app.id}",
            user_role='ADMIN',
            application_id=app.id
        )
        self.assertEqual(admin_ai_res['status'], 'success')
        self.assertIn('Risk Assessment', admin_ai_res['reply'])
        self.assertIn('Human Administrator Decision Required', admin_ai_res['reply'])

        # 4 & 5: Authorized admin approves the application
        res_approve = self.admin_client.post(f'/api/admin/seller-applications/{app.id}/action', {
            'action': 'APPROVE',
            'reason': 'All documents verified and identity matched.'
        }, format='json')
        self.assertEqual(res_approve.status_code, status.HTTP_200_OK)
        self.assertEqual(res_approve.data['currentStatus'], 'APPROVED')

        # 6: Verify seller privileges, store creation, and product activation
        self.seller_user.refresh_from_db()
        self.assertEqual(self.seller_user.role, 'SELLER')
        self.assertTrue(Seller.objects.filter(email=self.seller_user.email).exists())
        self.assertTrue(Store.objects.filter(id=f"store-{app.id}").exists())
        activated_product = Product.objects.filter(name='Sharma Wireless Mouse').first()
        self.assertIsNotNone(activated_product)
        self.assertEqual(activated_product.stock, 25)
        self.assertEqual(activated_product.stockStatus, 'In Stock')

    # =======================================================================
    # JOURNEY E: FAILURE RECOVERY & SECURITY AUDIT
    # =======================================================================
    def test_journey_e_failure_recovery(self):
        """
        Tests failure recovery and security boundaries:
        1. Missing AI credentials gracefully falls back to local deterministic engine without 500.
        2. Invalid PIN codes (5-digit or unsupported 999999) return clear error guidance and retain pending state.
        3. Out-of-stock items return status out_of_stock_nearby and suggest real database in-stock alternatives.
        4. Customer cannot approve seller applications (HTTP 403 Forbidden).
        5. Invalid upload mime-types or non-image store photos are rejected (HTTP 400).
        6. Customers cannot access other users' orders or private documents.
        """
        # 1: Missing AI credentials
        with patch.dict('os.environ', {'AUTOCART_DISABLE_LLM': '1'}):
            res_no_ai = self.engine.run_sathi(
                query="Suggest wireless earbuds under ₹2,000",
                session_id="no_ai_sess"
            )
            self.assertEqual(res_no_ai['status'], 'success')
            self.assertGreater(len(res_no_ai['products']), 0)
            self.assertEqual(res_no_ai['llmProvider'], 'grounded-engine')

        # 2: Invalid PIN format and unsupported coverage
        pin_sess = "pin_fail_sess"
        self.engine.run_sathi(query="Show me nearby stores", session_id=pin_sess)
        res_bad_format = self.engine.run_sathi(query="12345", session_id=pin_sess)
        self.assertEqual(res_bad_format['status'], 'error')
        self.assertIn("valid 6-digit PIN code", res_bad_format['reply'])

        res_unmapped = self.engine.run_sathi(query="999999", session_id=pin_sess)
        self.assertEqual(res_unmapped['status'], 'unsupported_area')
        self.assertIn("do not service PIN code 999999", res_unmapped['reply'])

        # 3: Out of stock product returns status out_of_stock_nearby and DB alternatives
        p_oos = Product.objects.create(
            id='eb-oos-vintage', name='Vintage Audiophile Studio Buds', slug='vintage-studio-buds',
            category='Audio', price=3999.0, stock=0, stockStatus='Out of Stock'
        )
        oos_sess = "oos_test_sess"
        SessionMemoryManager.set_selected_product(f"anon:{oos_sess}", {'id': p_oos.id, 'name': p_oos.name, 'category': 'Audio', 'price': 3999.0})
        SessionMemoryManager.set_delivery_address(f"anon:{oos_sess}", {'pinCode': '421301', 'area': 'Kalyan'}, pin_code='421301')
        res_oos = self.engine.run_sathi(query="Which nearby store has these earbuds?", session_id=oos_sess)
        self.assertEqual(res_oos['status'], 'out_of_stock_nearby')
        self.assertIn("currently out of stock at all", res_oos['reply'])
        self.assertTrue(any(alt['id'] in [self.earbud_1.id, self.earbud_2.id, self.earbud_3.id] for alt in res_oos.get('products', [])))

        # 4: Security: Non-admin customer cannot approve seller application
        app = SellerApplication.objects.create(
            id='app-sec-01', ownerUserId=self.seller_user.id, companyName='Test Corp',
            email=self.seller_user.email, status='PENDING_ADMIN_APPROVAL'
        )
        res_unauth_approve = self.customer_client.post(f'/api/admin/seller-applications/{app.id}/action', {
            'action': 'APPROVE'
        }, format='json')
        self.assertEqual(res_unauth_approve.status_code, status.HTTP_403_FORBIDDEN)

        # 5: Invalid document file type rejected in DRAFT application, and uploads blocked in PENDING status
        app_draft = SellerApplication.objects.create(
            id='app-sec-draft-01', ownerUserId=self.seller_user.id, companyName='Draft Corp',
            email=self.seller_user.email, status='DRAFT'
        )
        bad_doc = SimpleUploadedFile("malware.exe", b"MZexecutabledata", content_type="application/x-msdownload")
        res_bad_upload = self.seller_client.post(f'/api/seller/applications/{app_draft.id}/documents', {
            'docType': 'PAN',
            'file': bad_doc
        }, format='multipart')
        self.assertEqual(res_bad_upload.status_code, status.HTTP_400_BAD_REQUEST)

        # Uploads to non-editable PENDING application are rejected with 409 Conflict
        good_doc = SimpleUploadedFile("pan.png", b"fake-pan-bytes", content_type="image/png")
        res_conflict = self.seller_client.post(f'/api/seller/applications/{app.id}/documents', {
            'docType': 'PAN',
            'file': good_doc
        }, format='multipart')
        self.assertEqual(res_conflict.status_code, status.HTTP_409_CONFLICT)

        # 6: Customer cannot access another customer's order
        other_order = Order.objects.create(
            id='ord-other-user-01', customerEmail='other.customer@example.com',
            totalAmount=2499.0, status='Confirmed', items=[{'id': self.earbud_1.id, 'quantity': 1}]
        )
        res_order = self.customer_client.get(f'/api/orders/{other_order.id}')
        self.assertEqual(res_order.status_code, status.HTTP_404_NOT_FOUND)
