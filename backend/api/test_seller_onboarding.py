"""
Seller onboarding, permissions and security tests.
Document reading is replaced with fixed text so nothing here needs the OCR engine or the network.
"""

import shutil
import tempfile
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from api.models import Seller, SellerApplication, Store, User
from api.views import generate_token

TMP_MEDIA = tempfile.mkdtemp()

TEXTS = {
    'aadhaar': 'Government of India\nRahul Sharma\nDOB: 14/03/1991\nMALE\nXXXX XXXX 4821\nAddress: 12 Hill Road Andheri East Mumbai 400069',
    'aadhaar_full': 'Government of India\nRahul Sharma\nDOB: 14/03/1991\nMALE\n2345 6789 4821',
    'pan': 'INCOME TAX DEPARTMENT\nABCDE1234F\nName\nRahul Sharma\nFather\'s Name\nMohan Sharma\nDate of Birth\n14/03/1991',
    'pan_other': 'INCOME TAX DEPARTMENT\nZZZZZ9999Z\nName\nPriya Nair\nFather\'s Name\nSuresh Nair\nDate of Birth\n02/02/1990',
    'gst': 'GSTIN: 27ABCDE1234F1Z5\nLegal Name: Sharma Electronics',
    'addr': 'Sharma Electronics 12 Hill Road Andheri East Mumbai 400069',
    'bank': 'IFSC: HDFC0001234 A/c No 123456789012',
}


def fake_read_text(path, mime=''):
    name = path.replace('\\', '/').split('/')[-1].lower()
    for key in ('aadhaar_full', 'aadhaar', 'pan_other', 'pan', 'gst', 'addr', 'bank'):
        if key in name:
            return {'status': 'DONE', 'text': TEXTS[key]}
    return {'status': 'UNREADABLE', 'text': ''}


FORM = dict(
    companyName='Sharma Electronics', contactName='Rahul Sharma', email='shop@sharma.example', phone='9820012345',
    gstin='27ABCDE1234F1Z5', pan='ABCDE1234F', address='12 Hill Road, Andheri East', city='Mumbai', state='Maharashtra',
    pincode='400069', storeLatitude=19.1136, storeLongitude=72.8697, productCategories=['Electronics'],
    plannedProducts=[{'name': 'Wireless Mouse', 'category': 'Electronics', 'approxPrice': 999}],
)


def upload(client, app_id, doc_type, file_name, file_bytes=b'fake-image-bytes', content_type='image/png'):
    return client.post(
        f'/api/seller/applications/{app_id}/documents',
        {'docType': doc_type, 'file': SimpleUploadedFile(file_name, file_bytes, content_type=content_type)},
        format='multipart',
    )


@override_settings(MEDIA_ROOT=TMP_MEDIA)
class SellerOnboardingTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.customer = User.objects.create_user(email='buyer@example.com', name='Rahul Sharma', password='pw-12345', role='CUSTOMER')
        self.other = User.objects.create_user(email='other@example.com', name='Other Person', password='pw-12345', role='CUSTOMER')
        self.admin = User.objects.create_user(email='boss@example.com', name='Admin', password='pw-12345', role='ADMIN')
        self.guest, self.c, self.o, self.a = APIClient(), APIClient(), APIClient(), APIClient()
        self.c.credentials(HTTP_AUTHORIZATION='Bearer ' + generate_token(self.customer))
        self.o.credentials(HTTP_AUTHORIZATION='Bearer ' + generate_token(self.other))
        self.a.credentials(HTTP_AUTHORIZATION='Bearer ' + generate_token(self.admin))
        self.patcher = patch('api.seller_docs.read_text', side_effect=fake_read_text)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    # -- helpers --
    def start(self, **over):
        res = self.c.post('/api/seller/applications', {**FORM, **over}, format='json')
        self.assertEqual(res.status_code, 201, res.content)
        return res.json()['id']

    def upload_all(self, app_id, pan_file='pan.png'):
        for t, f in (('AADHAAR', 'aadhaar.png'), ('PAN', pan_file), ('GST_CERTIFICATE', 'gst.png'),
                     ('ADDRESS_PROOF', 'addr.png'), ('BANK_PROOF', 'bank.png'), ('STORE_PHOTO', 'shop.jpg')):
            self.assertEqual(upload(self.c, app_id, t, f).status_code, 201)

    # -- who can see what --
    def test_guest_cannot_list_or_apply(self):
        self.assertEqual(self.guest.get('/api/seller/applications').status_code, 401)
        self.assertEqual(self.guest.post('/api/seller/applications', FORM, format='json').status_code, 401)

    def test_customer_sees_only_their_own_application(self):
        app_id = self.start()
        self.assertEqual(len(self.c.get('/api/seller/applications').json()), 1)
        self.assertEqual(self.o.get('/api/seller/applications').json(), [])
        self.assertEqual(self.o.get(f'/api/seller/applications/{app_id}').status_code, 404)
        self.assertEqual(len(self.a.get('/api/seller/applications').json()), 1)

    def test_customer_cannot_take_admin_actions(self):
        app_id = self.start()
        res = self.c.post(f'/api/admin/seller-applications/{app_id}/action', {'action': 'APPROVE'}, format='json')
        self.assertEqual(res.status_code, 403)

    def test_bad_form_is_rejected_with_field_errors(self):
        res = self.c.post('/api/seller/applications', {**FORM, 'pan': '123', 'storeLatitude': None}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('pan', res.json()['errors'])
        self.assertIn('location', res.json()['errors'])

    # -- documents and Aadhaar privacy --
    def test_masked_aadhaar_stores_only_last_four_digits(self):
        app_id = self.start()
        res = upload(self.c, app_id, 'AADHAAR', 'aadhaar.png').json()
        self.assertEqual(res['ocrStatus'], 'DONE')
        self.assertEqual(res['extractedFields']['aadhaarMasked'], 'XXXX-XXXX-4821')
        self.assertEqual(SellerApplication.objects.get(id=app_id).aadhaarLast4, '4821')
        self.assertNotIn('2345', str(res))

    def test_unmasked_aadhaar_is_rejected_and_nothing_is_kept(self):
        app_id = self.start()
        res = upload(self.c, app_id, 'AADHAAR', 'aadhaar_full.png').json()
        self.assertEqual(res['ocrStatus'], 'REJECTED')
        self.assertEqual(res['extractedFields'], {})
        doc = SellerApplication.objects.get(id=app_id).documents.get(docType='AADHAAR')
        self.assertFalse(doc.file)
        self.assertNotIn('4821', doc.redactedText)
        self.assertNotIn('6789', doc.redactedText)

    def test_files_are_private(self):
        app_id = self.start()
        doc_id = upload(self.c, app_id, 'PAN', 'pan.png').json()['id']
        url = f'/api/seller/applications/{app_id}/documents/{doc_id}/file'
        self.assertEqual(self.guest.get(url).status_code, 401)
        self.assertEqual(self.o.get(url).status_code, 404)
        self.assertEqual(self.c.get(url).status_code, 200)
        self.assertEqual(self.a.get(url).status_code, 200)

    # -- submit decides the status --
    def test_missing_documents_need_more_information(self):
        app_id = self.start()
        upload(self.c, app_id, 'PAN', 'pan.png')
        res = self.c.post(f'/api/seller/applications/{app_id}/submit').json()
        self.assertEqual(res['status'], 'NEEDS_MORE_INFORMATION')
        self.assertIn('AADHAAR', res['missingDocuments'])

    def test_pan_mismatch_goes_to_manual_review(self):
        app_id = self.start()
        self.upload_all(app_id, pan_file='pan_other.png')
        res = self.c.post(f'/api/seller/applications/{app_id}/submit').json()
        self.assertEqual(res['status'], 'NEEDS_MANUAL_REVIEW')
        self.assertGreater(res['comparison']['mismatches'], 0)

    def test_complete_matching_application_waits_for_admin(self):
        app_id = self.start()
        self.upload_all(app_id)
        res = self.c.post(f'/api/seller/applications/{app_id}/submit').json()
        self.assertEqual(res['status'], 'PENDING_ADMIN_APPROVAL')
        self.assertEqual(res['comparison']['mismatches'], 0)

    # -- profile and decisions --
    def test_profile_has_location_products_and_masked_identity(self):
        app_id = self.start()
        self.upload_all(app_id)
        self.c.post(f'/api/seller/applications/{app_id}/submit')
        p = self.a.get(f'/api/seller/applications/{app_id}').json()
        self.assertEqual(p['store']['latitude'], 19.1136)
        self.assertEqual(p['plannedProducts'][0]['name'], 'Wireless Mouse')
        self.assertEqual(p['identity']['aadhaarMasked'], 'XXXX-XXXX-4821')
        self.assertEqual(p['identity']['pan'], 'ABCDE1234F')
        self.assertEqual(len(p['documents']), 6)

    def test_approval_creates_seller_store_and_role(self):
        app_id = self.start()
        self.upload_all(app_id)
        self.c.post(f'/api/seller/applications/{app_id}/submit')
        res = self.a.post(f'/api/admin/seller-applications/{app_id}/action', {'action': 'APPROVE'}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['currentStatus'], 'APPROVED')
        self.assertTrue(Seller.objects.filter(id=f'sel-{app_id}', status='Approved').exists())
        store = Store.objects.get(id=f'store-{app_id}')
        self.assertAlmostEqual(store.latitude, 19.1136)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.role, 'SELLER')

    def test_reject_needs_a_reason_and_shows_it_to_the_seller(self):
        app_id = self.start()
        self.upload_all(app_id)
        self.c.post(f'/api/seller/applications/{app_id}/submit')
        url = f'/api/admin/seller-applications/{app_id}/action'
        self.assertEqual(self.a.post(url, {'action': 'REJECT'}, format='json').status_code, 400)
        self.assertEqual(self.a.post(url, {'action': 'REJECT', 'reason': 'GST certificate is expired.'}, format='json').status_code, 200)
        mine = self.c.get(f'/api/seller/applications/{app_id}').json()
        self.assertEqual(mine['status'], 'REJECTED')
        self.assertEqual(mine['rejectionReason'], 'GST certificate is expired.')
        self.assertFalse(Store.objects.filter(id=f'store-{app_id}').exists())

    def test_cannot_approve_an_application_that_is_not_ready(self):
        app_id = self.start()  # still a draft
        res = self.a.post(f'/api/admin/seller-applications/{app_id}/action', {'action': 'APPROVE'}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_unsupported_file_extension(self):
        app_id = self.start()
        res = upload(self.c, app_id, 'PAN', 'malware.exe', file_bytes=b'fake-image-bytes', content_type='application/x-msdownload')
        self.assertEqual(res.status_code, 400)
        self.assertIn('Unsupported file extension', res.json()['detail'])

    def test_oversized_upload(self):
        app_id = self.start()
        big_bytes = b'fake-image' + (b'0' * (11 * 1024 * 1024))
        res = upload(self.c, app_id, 'PAN', 'pan.png', file_bytes=big_bytes, content_type='image/png')
        self.assertEqual(res.status_code, 400)
        self.assertIn('exceeds maximum allowed limit of 10 MB', res.json()['detail'])

    def test_executable_binary_rejection(self):
        app_id = self.start()
        mz_bytes = b'MZ\x90\x00' + b'\x00' * 100
        res_mz = upload(self.c, app_id, 'PAN', 'pan.png', file_bytes=mz_bytes, content_type='image/png')
        self.assertEqual(res_mz.status_code, 400)
        self.assertIn('Executable or script binary detected', res_mz.json()['detail'])

        elf_bytes = b'\x7fELF' + b'\x00' * 100
        res_elf = upload(self.c, app_id, 'PAN', 'pan.png', file_bytes=elf_bytes, content_type='image/png')
        self.assertEqual(res_elf.status_code, 400)
        self.assertIn('Executable or script binary detected', res_elf.json()['detail'])

    def test_unreadable_document_handling(self):
        app_id = self.start()
        res = upload(self.c, app_id, 'PAN', 'blurry_unknown.png')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()['ocrStatus'], 'UNREADABLE')
        # Complete remaining uploads but with unreadable PAN
        self.upload_all(app_id)
        upload(self.c, app_id, 'PAN', 'blurry_unknown.png')
        sub = self.c.post(f'/api/seller/applications/{app_id}/submit').json()
        self.assertEqual(sub['status'], 'NEEDS_MANUAL_REVIEW')

    def test_editable_ocr_fields_review(self):
        app_id = self.start()
        upload(self.c, app_id, 'PAN', 'pan.png')
        updated_form = {
            **FORM,
            'companyName': 'Sharma Electronics Superstore',
            'contactName': 'Rahul M. Sharma',
            'plannedProducts': [
                {'name': 'Mechanical Keyboard', 'category': 'Electronics', 'approxPrice': 2499, 'stock': 15}
            ]
        }
        res = self.c.post('/api/seller/applications', updated_form, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['companyName'], 'Sharma Electronics Superstore')
        self.assertEqual(res.json()['applicantName'], 'Rahul M. Sharma')
        self.assertEqual(res.json()['plannedProducts'][0]['name'], 'Mechanical Keyboard')

    def test_invalid_pan_and_gstin_formats_rejected(self):
        res_pan = self.c.post('/api/seller/applications', {**FORM, 'pan': 'INVALID123'}, format='json')
        self.assertEqual(res_pan.status_code, 400)
        self.assertIn('pan', res_pan.json()['errors'])

        res_gst = self.c.post('/api/seller/applications', {**FORM, 'gstin': 'INVALID_GSTIN'}, format='json')
        self.assertEqual(res_gst.status_code, 400)
        self.assertIn('gstin', res_gst.json()['errors'])

    def test_risk_score_deterministic_consistency(self):
        from api.risk_service import SellerRiskScoringService
        app_id = self.start()
        self.upload_all(app_id)
        app = SellerApplication.objects.get(id=app_id)
        docs = list(app.documents.all())
        score1 = SellerRiskScoringService.calculate_risk_score(app, docs)
        score2 = SellerRiskScoringService.calculate_risk_score(app, docs)
        self.assertEqual(score1['score'], score2['score'])
        self.assertEqual(score1['scoringVersion'], '2.1-deterministic')
        self.assertIn(score1['category'], ('Low', 'Medium', 'High'))
        self.assertIsInstance(score1['contributingFactors'], list)

    def test_risk_explanation_factor_breakdown(self):
        from api.agents.tools import AgentToolLibrary
        app_id = self.start()
        tool_lib = AgentToolLibrary()
        explanation = tool_lib.explain_application_risk(app_id, user_role='ADMIN')
        self.assertTrue(explanation['found'])
        self.assertEqual(explanation['applicationId'], app_id)
        self.assertIn('contributingFactors', explanation)
        self.assertIn('recommendedAction', explanation)
        self.assertIn('scoringVersion', explanation)
        self.assertGreater(explanation['riskScore'], 10)

    def test_admin_assistant_agent_f_queries(self):
        app_id = self.start()
        self.upload_all(app_id)
        self.c.post(f'/api/seller/applications/{app_id}/submit')

        # Customer forbidden
        res_cust = self.c.post('/api/ai/admin-assistant', {'prompt': 'Summarize pending applications'}, format='json')
        self.assertEqual(res_cust.status_code, 403)

        # Admin pending summary
        res_sum = self.a.post('/api/ai/admin-assistant', {'prompt': 'Summarize pending applications'}, format='json')
        self.assertEqual(res_sum.status_code, 200)
        self.assertEqual(res_sum.json()['status'], 'success')
        self.assertIn('summarize_pending_applications', res_sum.json()['toolsExecuted'])

        # Admin missing documents query
        res_missing = self.a.post('/api/ai/admin-assistant', {'prompt': 'Which applications have missing documents?'}, format='json')
        self.assertEqual(res_missing.status_code, 200)
        self.assertEqual(res_missing.json()['status'], 'success')
        self.assertIn('get_applications_with_missing_docs', res_missing.json()['toolsExecuted'])

        # Admin risk explanation query
        res_risk = self.a.post('/api/ai/admin-assistant', {'prompt': f'Explain the risk score for application {app_id}'}, format='json')
        self.assertEqual(res_risk.status_code, 200)
        self.assertEqual(res_risk.json()['status'], 'success')
        self.assertIn('explain_application_risk', res_risk.json()['toolsExecuted'])
        self.assertIn('riskAnalysis', res_risk.json())

    def test_admin_assistant_unknown_application_id(self):
        res = self.a.post('/api/ai/admin-assistant', {'prompt': 'Explain the risk score for application app-unknown999'}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['status'], 'not_found')
        self.assertIn('not found', res.json()['reply'].lower())

    def test_submission_with_only_mandatory_pan_and_masked_aadhaar(self):
        """Verifies that an application with ONLY PAN and masked Aadhaar cleanly enters PENDING_ADMIN_APPROVAL without requiring unrelated docs."""
        app_id = self.start()
        # Upload ONLY mandatory documents: AADHAAR and PAN
        self.assertEqual(upload(self.c, app_id, 'AADHAAR', 'aadhaar.png').status_code, 201)
        self.assertEqual(upload(self.c, app_id, 'PAN', 'pan.png').status_code, 201)
        
        # Submit application
        res = self.c.post(f'/api/seller/applications/{app_id}/submit')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'PENDING_ADMIN_APPROVAL')
        self.assertEqual(data['missingDocuments'], [])
        
        # Admin can approve it directly
        app_res = self.a.post(f'/api/admin/seller-applications/{app_id}/action', {'action': 'APPROVE'}, format='json')
        self.assertEqual(app_res.status_code, 200)
        self.assertEqual(app_res.json()['currentStatus'], 'APPROVED')

    def test_admin_audit_trail_recorded_on_decisions(self):
        """Verifies audit trail entries are logged in SellerApplicationAudit on actions."""
        from api.models import SellerApplicationAudit
        app_id = self.start()
        self.assertEqual(upload(self.c, app_id, 'AADHAAR', 'aadhaar.png').status_code, 201)
        self.assertEqual(upload(self.c, app_id, 'PAN', 'pan.png').status_code, 201)
        self.c.post(f'/api/seller/applications/{app_id}/submit')

        # Admin approves
        self.a.post(f'/api/admin/seller-applications/{app_id}/action', {'action': 'APPROVE'}, format='json')
        audit_approve = SellerApplicationAudit.objects.filter(application_id=app_id, action='APPROVE').first()
        self.assertIsNotNone(audit_approve)
        self.assertEqual(audit_approve.performedBy, 'boss@example.com')
        self.assertEqual(audit_approve.toStatus, 'APPROVED')

    def test_ai_assistant_unauthenticated_and_no_autonomous_approval(self):
        """AI assistant requires authentication and never alters application status autonomously."""
        app_id = self.start()
        self.assertEqual(upload(self.c, app_id, 'AADHAAR', 'aadhaar.png').status_code, 201)
        self.assertEqual(upload(self.c, app_id, 'PAN', 'pan.png').status_code, 201)
        self.c.post(f'/api/seller/applications/{app_id}/submit')

        # Unauthenticated request rejected
        res_unauth = self.guest.post('/api/ai/admin-assistant', {'prompt': 'Summarize pending applications'}, format='json')
        self.assertEqual(res_unauth.status_code, 401)

        # Asking assistant about the application does not approve it
        res_query = self.a.post('/api/ai/admin-assistant', {'prompt': f'Explain the risk score for application {app_id}'}, format='json')
        self.assertEqual(res_query.status_code, 200)
        app = SellerApplication.objects.get(id=app_id)
        self.assertEqual(app.status, 'PENDING_ADMIN_APPROVAL')  # Still pending, not approved

    def test_seller_application_prepare_endpoint(self):
        """Verifies the Seller Onboarding Agent prepares the application summary with real documents."""
        app_id = self.start()
        self.assertEqual(upload(self.c, app_id, 'AADHAAR', 'aadhaar.png').status_code, 201)
        self.assertEqual(upload(self.c, app_id, 'PAN', 'pan.png').status_code, 201)

        res = self.c.get(f'/api/seller/applications/{app_id}/prepare')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['agent'], 'seller-onboarding')
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['applicationId'], app_id)
        self.assertIn('riskScore', data)
        self.assertIn('checklist', data)
        self.assertIn('documentsSummary', data)
        self.assertGreaterEqual(len(data['documentsSummary']), 2)

    def test_admin_assistant_what_to_review_before_approving(self):
        """Verifies admin review assistant explains what to review before approving an application."""
        app_id = self.start()
        self.assertEqual(upload(self.c, app_id, 'AADHAAR', 'aadhaar.png').status_code, 201)
        self.assertEqual(upload(self.c, app_id, 'PAN', 'pan.png').status_code, 201)
        self.c.post(f'/api/seller/applications/{app_id}/submit')

        res = self.a.post('/api/ai/admin-assistant', {'prompt': f'What should I review before approving application {app_id}?'}, format='json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('explain_application_risk', data['toolsExecuted'])
        self.assertIn('Mandatory Review Checklist', data['reply'])
        self.assertIn('Aadhaar Document', data['reply'])
        self.assertIn('PAN Card', data['reply'])
        self.assertIn('Store Location', data['reply'])

    def test_optional_gstin_empty_succeeds(self):
        """Verifies that empty GSTIN is accepted and does not fail form validation."""
        form_no_gst = {**FORM, 'gstin': ''}
        res = self.c.post('/api/seller/applications', form_no_gst, format='json')
        self.assertEqual(res.status_code, 201)
        app_id = res.json()['id']
        app = SellerApplication.objects.get(id=app_id)
        self.assertEqual(app.gstin, '')

    def test_pan_header_filtering_extracts_real_name(self):
        """Verifies parse_pan and _looks_like_name reject fused header strings like GOVTOFINDIA."""
        from api.seller_docs import parse_pan
        fused_text = (
            "INCOME TAX DEPARTMENT\n"
            "GOVTOFINDIA\n"
            "Name\n"
            "RAHUL SHARMA\n"
            "Father's Name\n"
            "RAMESH SHARMA\n"
            "Permanent Account Number\n"
            "ABCDE1234F"
        )
        parsed = parse_pan(fused_text)
        self.assertEqual(parsed['pan'], 'ABCDE1234F')
        self.assertEqual(parsed['name'], 'Rahul Sharma')
        self.assertNotEqual(parsed['name'], 'Govtofindia')
        self.assertEqual(parsed['fatherName'], 'Ramesh Sharma')

    def test_document_upload_syncs_fields_to_application_model(self):
        """Uploading PAN and Aadhaar automatically synchronizes extracted fields to the application."""
        # Start application with default user name
        start_res = self.c.post('/api/seller/applications/start')
        self.assertEqual(start_res.status_code, 201)
        app_id = start_res.json()['id']

        # Upload PAN
        pan_res = upload(self.c, app_id, 'PAN', 'pan.png')
        self.assertEqual(pan_res.status_code, 201)

        app = SellerApplication.objects.get(id=app_id)
        self.assertEqual(app.pan, 'ABCDE1234F')
        self.assertEqual(app.applicantName, 'Rahul Sharma')

        # Upload Aadhaar
        aadhaar_res = upload(self.c, app_id, 'AADHAAR', 'aadhaar.png')
        self.assertEqual(aadhaar_res.status_code, 201)
        app.refresh_from_db()
        self.assertEqual(app.aadhaarLast4, '4821')
        # Separated residential address: extracted from Aadhaar into residentialAddress, leaving store address clean
        self.assertIn('Hill Road', app.residentialAddress)
        self.assertEqual(app.residentialPincode, '400069')
        self.assertEqual(app.address, '')

    def test_aadhaar_disclaimer_patterns_never_become_address(self):
        """Aadhaar disclaimer text and UIDAI helpline text are scrubbed and never populate address fields."""
        from api.seller_docs import parse_aadhaar
        raw_with_disclaimers = (
            "GOVERNMENT OF INDIA\n"
            "Rahul Sharma\n"
            "DOB: 14/03/1991\n"
            "MALE\n"
            "XXXX XXXX 4821\n"
            "Address: 12 Hill Road Andheri East Mumbai 400069\n"
            "Aadhaar is a proof of identity, not of citizenship or date of birth.\n"
            "To update your address visit uidai.gov.in or call 1947.\n"
            "help@uidai.gov.in"
        )
        parsed = parse_aadhaar(raw_with_disclaimers)
        self.assertEqual(parsed['aadhaarLast4'], '4821')
        self.assertIn('12 Hill Road', parsed['address'])
        self.assertNotIn('citizenship', parsed['address'].lower())
        self.assertNotIn('uidai.gov.in', parsed['address'].lower())
        self.assertNotIn('1947', parsed['address'])
        self.assertNotIn('help@', parsed['address'].lower())

    def test_wrong_document_type_rejection(self):
        """Uploading PAN under AADHAAR docType is detected and rejected."""
        start_res = self.c.post('/api/seller/applications/start')
        app_id = start_res.json()['id']

        # Upload PAN content under AADHAAR
        res = upload(self.c, app_id, 'AADHAAR', 'pan.png')
        self.assertEqual(res.status_code, 201)
        doc_data = res.json()
        self.assertEqual(doc_data['ocrStatus'], 'REJECTED')
        self.assertTrue(any('PAN card' in w for w in doc_data.get('warnings', [])))

    def test_step_validation_allows_advancing_without_products_in_stage_1(self):
        """Step 1 validation allows advancing without plannedProducts or location coordinates."""
        stage1_payload = {
            'stage': 'STAGE_1',
            'companyName': 'Sharma Electronics',
            'contactName': 'Rahul Sharma',
            'email': 'shop@sharma.example',
            'phone': '9820012345',
            'pan': 'ABCDE1234F',
            'businessType': 'Retailer',
            'residentialAddress': '12 Hill Road, Andheri East',
            'residentialPincode': '400069',
        }
        res = self.c.post('/api/seller/applications', stage1_payload, format='json')
        self.assertEqual(res.status_code, 201, res.content)
        app = SellerApplication.objects.get(id=res.json()['id'])
        self.assertEqual(app.companyName, 'Sharma Electronics')
        self.assertEqual(app.residentialPincode, '400069')

        # But advancing to STAGE_2 requires store address, pincode, and valid location
        stage2_invalid = {
            'stage': 'STAGE_2',
            'address': '',
            'pincode': '',
        }
        res2 = self.c.post('/api/seller/applications', stage2_invalid, format='json')
        self.assertEqual(res2.status_code, 400)
        self.assertIn('address', res2.json()['errors'])
        self.assertIn('pincode', res2.json()['errors'])
        self.assertIn('location', res2.json()['errors'])

    def test_pincode_lookup_endpoint(self):
        """PIN code lookup returns postal details for valid PINs and 404 for nonexistent PINs."""
        # Valid PIN code
        res_valid = self.c.get('/api/location/pincode-lookup?pincode=400069')
        self.assertEqual(res_valid.status_code, 200)
        data = res_valid.json()
        self.assertEqual(data['pincode'], '400069')
        self.assertIn('Mumbai', data['district'])
        self.assertEqual(data['state'], 'Maharashtra')
        self.assertIn('lat', data['centroid'])
        self.assertIn('lng', data['centroid'])

        # Nonexistent PIN code (never fabricate data)
        res_invalid = self.c.get('/api/location/pincode-lookup?pincode=999999')
        self.assertEqual(res_invalid.status_code, 404)

        # Malformed PIN code
        res_bad = self.c.get('/api/location/pincode-lookup?pincode=123')
        self.assertEqual(res_bad.status_code, 400)

    def test_reverse_geocode_endpoint(self):
        """Reverse geocode endpoint returns area/neighborhood confirmation."""
        res = self.c.get('/api/location/reverse-geocode?lat=19.1136&lng=72.8697')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn('area', data)
        self.assertIn('city', data)

    def test_deterministic_name_matching_variations_and_mismatches(self):
        """Tests deterministic name matching across formatting variations and conflicting names."""
        from api.seller_docs import _names_match, normalize_name

        # Normalization
        self.assertEqual(normalize_name("Dr. Rahul  Sharma"), "rahul sharma")
        self.assertEqual(normalize_name("Shri R.K. Narayan"), "r k narayan")

        # Safe variations that MUST match
        self.assertTrue(_names_match("Rahul Sharma", "Rahul Sharma"))
        self.assertTrue(_names_match("RAHUL SHARMA", "rahul sharma"))
        self.assertTrue(_names_match("Dr. Rahul Sharma", "Rahul Sharma"))
        self.assertTrue(_names_match("Rahul Mohan Sharma", "Rahul Sharma"))
        self.assertTrue(_names_match("R. Sharma", "Rahul Sharma"))
        self.assertTrue(_names_match("Sharma Rahul", "Rahul Sharma"))
        self.assertTrue(_names_match("RahulSharma", "Rahul Sharma"))

        # Genuinely different people with shared surnames MUST NOT match
        self.assertFalse(_names_match("Rahul Sharma", "Priya Sharma"))
        self.assertFalse(_names_match("Rahul Sharma", "Mohan Sharma"))
        self.assertFalse(_names_match("Rahul Sharma", "Rahul Verma"))
        self.assertFalse(_names_match("Amit Patel", "Suresh Patel"))

    def test_store_pin_does_not_mismatch_with_different_residential_pin(self):
        """A seller's store PIN in Bandra (400050) does not mismatch with their Aadhaar residential PIN in Andheri (400069)."""
        from api.seller_docs import compare_application
        app = SellerApplication.objects.create(
            id='app-pin-test-1',
            ownerUserId=self.customer.id,
            applicantName='Rahul Sharma',
            residentialAddress='12 Hill Road, Andheri East',
            residentialPincode='400069',
            address='Shop 5, Linking Road, Bandra West',
            pincode='400050',
            storeLatitude=19.0596,
            storeLongitude=72.8295,
            pan='ABCDE1234F',
        )
        # Fake Aadhaar doc
        aadhaar_doc = type('Doc', (), {
            'docType': 'AADHAAR',
            'ocrStatus': 'DONE',
            'extractedFields': {
                'name': 'Rahul Sharma',
                'pincode': '400069',
                'residentialPincode': '400069',
                'aadhaarLast4': '4821',
            }
        })()
        pan_doc = type('Doc', (), {
            'docType': 'PAN',
            'ocrStatus': 'DONE',
            'extractedFields': {
                'name': 'Rahul Sharma',
                'pan': 'ABCDE1234F',
            }
        })()

        res = compare_application(app, [aadhaar_doc, pan_doc])
        # Check that there are NO mismatches on PIN code
        mismatch_labels = [c['label'] for c in res['checks'] if c['status'] == 'mismatch']
        self.assertNotIn('Store PIN code matches the documents', mismatch_labels)
        self.assertEqual(res['mismatches'], 0)
        self.assertEqual(res['riskCategory'], 'Low')

    def test_negative_user_intent_does_not_trigger_unrelated_product_search(self):
        """When a user responds with 'No' or 'No thanks', Sathi does not search for products."""
        from api.agents.engine import agent_engine
        res = agent_engine.run_sathi("No", session_id="test-no-session")
        self.assertEqual(res['status'], 'success')
        self.assertEqual(res['products'], [])
        self.assertIn('No problem', res['reply'])
        self.assertNotIn('search_products', res['toolsExecuted'])

    def test_mobile_phone_search_does_not_return_headphones(self):
        """Searching for phones/smartphones excludes audio headphones and earbuds."""
        from api.agents.tools import search_products
        res = search_products("mobile phone under 30000")
        for p in res.get('products', []):
            name_lower = p['name'].lower()
            self.assertNotIn('headphone', name_lower)
            self.assertNotIn('earbuds', name_lower)
            self.assertNotIn('airpods', name_lower)



class RealRapidOCRTests(TestCase):
    def test_real_rapidocr_png_image_and_pdf(self):
        """Tests unmocked RapidOCR execution on real synthetic PNG and PDF files."""
        import os
        from PIL import Image, ImageDraw
        try:
            import pymupdf as fitz
        except ImportError:
            fitz = None
        from api.seller_docs import read_text

        # 1. Real Image test
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as img_file:
            img = Image.new('RGB', (600, 250), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            draw.text((20, 30), 'INCOME TAX DEPARTMENT', fill=(0, 0, 0))
            draw.text((20, 80), 'ABCDE1234F', fill=(0, 0, 0))
            draw.text((20, 130), 'RAHUL SHARMA', fill=(0, 0, 0))
            img.save(img_file.name)
            img_path = img_file.name

        try:
            res_img = read_text(img_path, 'image/png')
            self.assertEqual(res_img['status'], 'DONE')
            self.assertIn('ABCDE1234F', res_img['text'])
        finally:
            if os.path.exists(img_path):
                os.remove(img_path)

        # 2. Real PDF test rendered via PyMuPDF (if installed)
        if fitz is not None:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
                pdf_path = pdf_file.name

            doc = fitz.open()
            page = doc.new_page(width=500, height=300)
            page.insert_text((40, 50), 'GOVERNMENT OF INDIA')
            page.insert_text((40, 100), 'XXXX XXXX 4821')
            page.insert_text((40, 150), 'RAHUL SHARMA')
            doc.save(pdf_path)
            doc.close()

            try:
                res_pdf = read_text(pdf_path, 'application/pdf')
                self.assertEqual(res_pdf['status'], 'DONE')
                self.assertIn('4821', res_pdf['text'])
            finally:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

    def test_pan_parsing_and_father_name_ordering(self):
        """Verifies parse_pan correctly extracts cardholder vs father name even in reversed or glued OCR text."""
        from api.seller_docs import parse_pan

        # 1. Standard forward layout
        sample_forward = (
            "INCOME TAX DEPARTMENT\n"
            "Permanent Account Number Card\n"
            "ABCDE1234F\n"
            "Name\n"
            "ASHWIN ANAND AGRAWAL\n"
            "Father's Name\n"
            "ANAND NANDKISHOR AGRAWAL\n"
            "Date of Birth\n"
            "30/12/2005\n"
        )
        res1 = parse_pan(sample_forward)
        self.assertEqual(res1['pan'], 'ABCDE1234F')
        self.assertEqual(res1['name'], 'Ashwin Anand Agrawal')
        self.assertEqual(res1['fatherName'], 'Anand Nandkishor Agrawal')
        self.assertEqual(res1['dob'], '30/12/2005')

        # 2. Inverted bottom-to-top layout with glued tokens
        sample_inverted = (
            "30/12/2005\n"
            "Date of Birth\n"
            "ANAND NANDKISHORAGRAWAL\n"
            "Father's Name\n"
            "ASHWINANANDAGRAWAL\n"
            "/Name\n"
            "INCOME TAX DEPARTMENT\n"
            "Permanent Account Number Card\n"
            "FTEPA3675M\n"
        )
        res2 = parse_pan(sample_inverted)
        self.assertEqual(res2['pan'], 'FTEPA3675M')
        self.assertEqual(res2['name'], 'Ashwin Anand Agrawal')
        self.assertEqual(res2['fatherName'], 'Anand Nandkishor Agrawal')
        self.assertEqual(res2['dob'], '30/12/2005')



class SecurityTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(email='buyer@example.com', name='Buyer', password='secret-pass', role='CUSTOMER')
        self.nopass = User.objects.create_user(email='nopass@example.com', name='No Password', role='CUSTOMER')
        self.admin = User.objects.create_user(email='boss@example.com', name='Boss', password='boss-pass', role='ADMIN')
        self.client = APIClient()

    def login(self, email, password):
        return self.client.post('/api/auth/login', {'email': email, 'password': password}, format='json')

    def test_no_master_password(self):
        self.assertEqual(self.login('buyer@example.com', 'admin123').status_code, 401)
        self.assertEqual(self.login('buyer@example.com', 'password').status_code, 401)
        self.assertEqual(self.login('nopass@example.com', 'anything').status_code, 401)
        self.assertEqual(self.login('buyer@example.com', 'secret-pass').status_code, 200)

    def test_admin_only_endpoints(self):
        token = self.login('buyer@example.com', 'secret-pass').json()['token']
        for url in ('/api/users', '/api/admin/stats', '/api/coupons'):
            self.assertEqual(self.client.get(url).status_code, 403, url)
            self.assertEqual(self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}').status_code, 403, url)
        admin_token = self.login('boss@example.com', 'boss-pass').json()['token']
        self.assertEqual(self.client.get('/api/users', HTTP_AUTHORIZATION=f'Bearer {admin_token}').status_code, 200)

    def test_catalogue_is_read_only_for_customers(self):
        token = self.login('buyer@example.com', 'secret-pass').json()['token']
        self.assertEqual(self.client.get('/api/products').status_code, 200)
        res = self.client.post('/api/products', {'id': 'x', 'name': 'x', 'slug': 'x'}, format='json', HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(res.status_code, 403)

    def test_orders_are_private(self):
        from api.models import Order
        Order.objects.create(id='ORD-1', customerName='Buyer', customerEmail='buyer@example.com')
        Order.objects.create(id='ORD-2', customerName='Someone', customerEmail='someone@example.com')
        self.assertEqual(self.client.get('/api/orders').status_code, 401)
        token = self.login('buyer@example.com', 'secret-pass').json()['token']
        auth = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        ids = [o['id'] for o in self.client.get('/api/orders', {'email': 'someone@example.com'}, **auth).json()]
        self.assertEqual(ids, ['ORD-1'])  # asking for someone else's email changes nothing
        self.assertEqual(self.client.get('/api/orders/ORD-2', **auth).status_code, 404)
        self.assertEqual(self.client.delete('/api/orders/ORD-1', **auth).status_code, 403)
