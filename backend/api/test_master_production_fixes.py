"""
Tests for AutoCart Master Production Fixes:
- Locality geocoding & coordinate synchronization (Issue 2)
- 2 of 2 Document counts (Issue 3)
- Document file endpoint authentication & inline viewing (Issue 4)
- Agent F Admin Workflows & Human Confirmation Mandate (Issue 6)
"""

import json
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import User, SellerApplication, SellerDocument, SellerApplicationAudit, Seller, Store
from api.views import generate_token
from api.location_service import lookup_pincode_details, geocode_address
from api.agents.engine import agent_engine


class MasterProductionFixesTests(TestCase):
    def setUp(self):
        self.c = Client()
        self.admin = User.objects.create(
            id='usr-admin-test',
            email='admin@autocart.com',
            name='Super Admin',
            role='ADMIN',
            phone='9999999999'
        )
        self.admin_token = generate_token(self.admin)

        self.seller_user = User.objects.create(
            id='usr-seller-test',
            email='rahul@amart.com',
            name='Rahul Sharma',
            role='BUYER',
            phone='9888888888'
        )
        self.seller_token = generate_token(self.seller_user)

        self.app = SellerApplication.objects.create(
            id='app-amart-001',
            ownerUserId=self.seller_user.id,
            companyName='Amart Electronics',
            storeName='Amart Electronics Kalyan',
            applicantName='Rahul Sharma',
            email='rahul@amart.com',
            phone='9888888888',
            pan='ABCDE1234F',
            status='PENDING_ADMIN_APPROVAL',
            pincode='421301',
            city='Kalyan',
            addressState='Maharashtra',
            address='Khadakpada',
            storeLatitude=19.2551,
            storeLongitude=73.1378,
            riskScore=35,
            riskCategory='Low',
            plannedProducts=[{'name': 'Boat Airdopes 141', 'category': 'Electronics', 'approxPrice': 1299, 'stock': 20}]
        )

        self.high_risk_app = SellerApplication.objects.create(
            id='app-risky-002',
            companyName='Shady Goods Traders',
            storeName='Shady Goods',
            applicantName='Vikram Singh',
            email='vikram@shady.com',
            phone='9777777777',
            pan='XYZAB9999Z',
            status='PENDING_ADMIN_APPROVAL',
            pincode='421301',
            city='Kalyan',
            riskScore=75,
            riskCategory='High'
        )

    # =========================================================================
    # ISSUE 2: LOCALITY GEOCODING & MAP POSITIONING
    # =========================================================================
    def test_pincode_421301_returns_localities_and_coordinates(self):
        details = lookup_pincode_details('421301')
        self.assertIsNotNone(details)
        self.assertTrue(details['valid'])
        self.assertIn('Birla College', details['localities'])
        self.assertIn('Chikanghar', details['localities'])
        self.assertIn('Godrej Hill', details['localities'])
        self.assertIn('Khadakpada', details['localities'])
        self.assertIn('Wayle Nagar', details['localities'])

        coords_map = details.get('localityCoordinates', {})
        self.assertIn('Birla College', coords_map)
        self.assertAlmostEqual(coords_map['Birla College']['lat'], 19.2482, places=3)
        self.assertAlmostEqual(coords_map['Birla College']['lng'], 73.1465, places=3)

    def test_geocode_endpoint_resolves_localities(self):
        res = self.c.get('/api/location/geocode?q=Birla+College&pincode=421301&city=Kalyan')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertAlmostEqual(data['latitude'], 19.2482, places=3)
        self.assertAlmostEqual(data['longitude'], 73.1465, places=3)

    def test_different_localities_have_distinct_coordinates(self):
        geo1 = geocode_address('Birla College', pincode='421301')
        geo2 = geocode_address('Godrej Hill', pincode='421301')
        self.assertIsNotNone(geo1)
        self.assertIsNotNone(geo2)
        self.assertNotEqual((geo1['latitude'], geo1['longitude']), (geo2['latitude'], geo2['longitude']))

    # =========================================================================
    # ISSUE 3: 2 OF 2 REQUIRED DOCUMENT COUNT (NO 6 DOCUMENTS)
    # =========================================================================
    def test_applications_view_returns_2_of_2_document_metrics(self):
        # Create 1 mandatory document
        SellerDocument.objects.create(
            id='doc-aadhaar-1',
            application=self.app,
            docType='AADHAAR',
            fileName='aadhaar.png',
            ocrStatus='DONE'
        )

        res = self.c.get('/api/seller/applications', HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        self.assertEqual(res.status_code, 200)
        apps = res.json()
        target = next(a for a in apps if a['id'] == self.app.id)
        self.assertEqual(target['requiredDocumentCount'], 1)
        self.assertEqual(target['totalRequiredDocuments'], 2)
        self.assertEqual(target['optionalDocumentCount'], 0)
        self.assertEqual(target['documentCount'], 1)

    # =========================================================================
    # ISSUE 4: UPLOADED DOCUMENTS OPENING WITH TOKEN AUTH & INLINE DISPOSITION
    # =========================================================================
    def test_document_file_endpoint_with_query_param_token(self):
        dummy_file = SimpleUploadedFile("pan_card.png", b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR", content_type="image/png")
        doc = SellerDocument.objects.create(
            id='doc-pan-123',
            application=self.app,
            docType='PAN',
            fileName='pan_card.png',
            file=dummy_file,
            mimeType='image/png',
            ocrStatus='DONE'
        )

        # GET request using query param ?token=... (as when opening in browser tab)
        res = self.c.get(f'/api/seller/applications/{self.app.id}/documents/{doc.id}/file?token={self.admin_token}')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'image/png')
        self.assertIn('inline', res['Content-Disposition'])

    # =========================================================================
    # ISSUE 6: AGENT F ADMIN WORKFLOWS & HUMAN CONFIRMATION
    # =========================================================================
    def test_agent_f_find_all_pending_applications(self):
        res = agent_engine.run_admin_assistance_agent('Find all pending applications', user_role='ADMIN')
        self.assertEqual(res['status'], 'success')
        self.assertIn('applications', res)
        app_ids = [a['id'] for a in res['applications']]
        self.assertIn(self.app.id, app_ids)
        self.assertIn(self.high_risk_app.id, app_ids)

    def test_agent_f_approve_requires_confirmation(self):
        # Initial request without confirmation
        res = agent_engine.run_admin_assistance_agent('Approve amart electronics', user_role='ADMIN')
        self.assertEqual(res['status'], 'confirmation_required')
        self.assertTrue(res['requiresConfirmation'])
        self.assertEqual(res['action'], 'APPROVE')
        self.assertEqual(res['applicationId'], self.app.id)

        # Check DB was NOT modified prematurely
        self.app.refresh_from_db()
        self.assertEqual(self.app.status, 'PENDING_ADMIN_APPROVAL')

    def test_agent_f_approve_executes_when_confirmed(self):
        # Confirmed execution
        res = agent_engine.run_admin_assistance_agent(
            'confirm approve amart electronics',
            user_role='ADMIN',
            application_id=self.app.id,
            user_email=self.admin.email,
            confirmed=True,
            action='APPROVE'
        )
        self.assertEqual(res['status'], 'success')

        # Check DB persistence
        self.app.refresh_from_db()
        self.assertEqual(self.app.status, 'APPROVED')

        # Check Seller and Store creation
        seller = Seller.objects.filter(id=f"sel-{self.app.id}").first()
        self.assertIsNotNone(seller)
        self.assertEqual(seller.status, 'Approved')

        store = Store.objects.filter(id=f"store-{self.app.id}").first()
        self.assertIsNotNone(store)
        self.assertEqual(store.operatingStatus, 'Open')

        # Check audit trail
        audit = SellerApplicationAudit.objects.filter(application=self.app, action='APPROVE').first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.toStatus, 'APPROVED')

    def test_agent_f_remove_sellers_with_risk_score_gt_50_workflow(self):
        # 1. Unconfirmed request
        res = agent_engine.run_admin_assistance_agent(
            'Remove sellers who have risk score more than 50',
            user_role='ADMIN'
        )
        self.assertEqual(res['status'], 'confirmation_required')
        self.assertTrue(res['requiresConfirmation'])
        self.assertEqual(res['threshold'], 50)
        self.assertEqual(res['affectedCount'], 1)
        self.assertEqual(res['affectedApplications'][0]['id'], self.high_risk_app.id)

        # Ensure high-risk seller is not yet removed
        self.high_risk_app.refresh_from_db()
        self.assertEqual(self.high_risk_app.status, 'PENDING_ADMIN_APPROVAL')

        # 2. Confirmed request
        res_confirmed = agent_engine.run_admin_assistance_agent(
            'confirm remove sellers who have risk score more than 50',
            user_role='ADMIN',
            user_email=self.admin.email,
            confirmed=True,
            action='REMOVE_HIGH_RISK_SELLERS'
        )
        self.assertEqual(res_confirmed['status'], 'success')

        # Ensure high-risk seller was rejected/suspended in database
        self.high_risk_app.refresh_from_db()
        self.assertEqual(self.high_risk_app.status, 'REJECTED')

        # Low risk seller (risk 35 <= 50) was NOT touched
        self.app.refresh_from_db()
        self.assertNotEqual(self.app.status, 'REJECTED')

    def test_agent_f_show_approved_and_rejected(self):
        # Mark app as approved
        self.app.status = 'APPROVED'
        self.app.save()

        res_app = agent_engine.run_admin_assistance_agent('Show all approved sellers', user_role='ADMIN')
        self.assertEqual(res_app['status'], 'success')
        self.assertTrue(any(a['id'] == self.app.id for a in res_app['applications']))

        # Mark risky app as rejected
        self.high_risk_app.status = 'REJECTED'
        self.high_risk_app.save()

        res_rej = agent_engine.run_admin_assistance_agent('Show rejected applications', user_role='ADMIN')
        self.assertEqual(res_rej['status'], 'success')
        self.assertTrue(any(a['id'] == self.high_risk_app.id for a in res_rej['applications']))
