import os
from django.test import TestCase
from api.seller_docs import (
    parse_pan,
    _split_glued_pan_names,
    _group_ocr_items_into_lines,
    remediate_pan_documents_and_applications,
)
from api.models import User, SellerApplication, SellerDocument


class PanOcrNameSpacingTests(TestCase):
    def test_glued_pan_name_and_father_name_splitting(self):
        """Verifies glued tokens like SHIVAMCHANDRAPRAKASHMISHRA are split into proper spaced names."""
        sample = (
            "INCOME TAX DEPARTMENT\n"
            "GOVT. OF INDIA\n"
            "Permanent Account Number Card\n"
            "KBCPM8395F\n"
            "/Name\n"
            "SHIVAMCHANDRAPRAKASHMISHRA\n"
            "/Father's Name\n"
            "CHANDRAPRAKASHMISHRA\n"
            "/Date of Birth\n"
            "05/06/2007\n"
        )
        res = parse_pan(sample)
        self.assertEqual(res['pan'], 'KBCPM8395F')
        self.assertEqual(res['name'], 'Shivam Chandraprakash Mishra')
        self.assertEqual(res['fatherName'], 'Chandraprakash Mishra')
        self.assertEqual(res['dob'], '05/06/2007')
        self.assertFalse(res.get('isAmbiguous'))

    def test_patronymic_family_surname_splitting(self):
        """Verifies patronymic surname sharing like Ashwin Anand Agrawal is de-glued properly."""
        sample = (
            "INCOME TAX DEPARTMENT\n"
            "Permanent Account Number Card\n"
            "FTEPA3675M\n"
            "/Name\n"
            "ASHWINANANDAGRAWAL\n"
            "/Father's Name\n"
            "ANANDNANDKISHORAGRAWAL\n"
            "Date of Birth\n"
            "30/12/2005\n"
        )
        res = parse_pan(sample)
        self.assertEqual(res['pan'], 'FTEPA3675M')
        self.assertEqual(res['name'], 'Ashwin Anand Agrawal')
        self.assertEqual(res['fatherName'], 'Anand Nandkishor Agrawal')
        self.assertEqual(res['dob'], '30/12/2005')

    def test_already_spaced_names_are_preserved(self):
        """Valid already-spaced names must not be modified or over-split."""
        sample = (
            "INCOME TAX DEPARTMENT\n"
            "Permanent Account Number Card\n"
            "ABCDE1234F\n"
            "Name\n"
            "RAHUL SHARMA\n"
            "Father's Name\n"
            "MOHAN SHARMA\n"
            "Date of Birth\n"
            "15/08/1990\n"
        )
        res = parse_pan(sample)
        self.assertEqual(res['name'], 'Rahul Sharma')
        self.assertEqual(res['fatherName'], 'Mohan Sharma')

    def test_layout_aware_line_grouping_joins_horizontal_fragments(self):
        """Tests that OCR bounding boxes on the same horizontal line are reconstructed with spaces."""
        box1 = [[10, 100], [50, 100], [50, 130], [10, 130]]
        box2 = [[55, 102], [120, 102], [120, 131], [55, 131]]
        box3 = [[125, 99], [180, 99], [180, 129], [125, 129]]
        items = [
            [box1, 'SHIVAM', 0.95],
            [box2, 'CHANDRAPRAKASH', 0.94],
            [box3, 'MISHRA', 0.96]
        ]
        grouped = _group_ocr_items_into_lines(items)
        self.assertEqual(len(grouped), 1)
        self.assertEqual(grouped[0]['text'], 'SHIVAM CHANDRAPRAKASH MISHRA')

    def test_multiline_fragments_between_labels_are_combined(self):
        """Tests that when a name spans multiple lines between labels, all fragments are combined with spaces."""
        sample = (
            "INCOME TAX DEPARTMENT\n"
            "GOVT. OF INDIA\n"
            "Permanent Account Number Card\n"
            "ABCDE1234F\n"
            "Name\n"
            "SHIVAM\n"
            "CHANDRAPRAKASH MISHRA\n"
            "Father's Name\n"
            "CHANDRAPRAKASH\n"
            "MISHRA\n"
            "Date of Birth\n"
            "05/06/2007\n"
        )
        res = parse_pan(sample)
        self.assertEqual(res['name'], 'Shivam Chandraprakash Mishra')
        self.assertEqual(res['fatherName'], 'Chandraprakash Mishra')

    def test_camel_case_word_splitting(self):
        """Tests that CamelCase concatenated names are separated properly."""
        name, father, amb = _split_glued_pan_names('ShivamChandraprakashMishra', 'ChandraprakashMishra')
        self.assertEqual(name, 'Shivam Chandraprakash Mishra')
        self.assertEqual(father, 'Chandraprakash Mishra')
        self.assertFalse(amb)

    def test_corroboration_with_context_names(self):
        """Verifies that corroborating names from Aadhaar or registration are used to segment tokens cleanly."""
        res = parse_pan(
            "Name\nSHIVAMCHANDRAPRAKASHMISHRA\nFather's Name\nCHANDRAPRAKASHMISHRA\nDOB 05/06/2007\nKBCPM8395F",
            context={'applicantName': 'Shivam Chandra Prakash Mishra'}
        )
        self.assertIn('Shivam', res['name'])
        self.assertIn('Mishra', res['name'])
        self.assertTrue(' ' in res['name'])

    def test_ambiguous_unknown_long_token_flags_review(self):
        """Tests that random/unknown long unsegmented strings are flagged for manual review without hallucinating."""
        _, _, amb = _split_glued_pan_names('Xyzwabcdefghijk', 'Qwertyuasdfghjk')
        self.assertTrue(amb)

    def test_remediation_function_corrects_stored_records(self):
        """Verifies database remediation correctly updates SellerDocument and SellerApplication."""
        user = User.objects.create_user(email='test_seller_remed@test.com', name='Test Seller', role='SELLER')
        app = SellerApplication.objects.create(
            id='app-test-remed-1',
            ownerUserId=user.id,
            applicantName='Shivam Chandraprakashmishra',
            email=user.email,
            phone='9999999999',
            pan='KBCPM8395F',
            identityDetails={
                'pan': 'KBCPM8395F',
                'panName': 'Shivam Chandraprakashmishra',
                'fatherName': 'Chandraprakashmishra'
            },
            ocrExtractedData={
                'PAN': {
                    'pan': 'KBCPM8395F',
                    'name': 'Shivam Chandraprakashmishra',
                    'fatherName': 'Chandraprakashmishra'
                }
            }
        )
        doc = SellerDocument.objects.create(
            id='doc-test-remed-1',
            application=app,
            docType='PAN',
            fileName='test_pan.jpg',
            ocrStatus='DONE',
            extractedFields={
                'pan': 'KBCPM8395F',
                'name': 'Shivam Chandraprakashmishra',
                'fatherName': 'Chandraprakashmishra'
            }
        )

        res = remediate_pan_documents_and_applications()
        self.assertGreaterEqual(res['remediated_docs'], 1)

        doc.refresh_from_db()
        self.assertEqual(doc.extractedFields['name'], 'Shivam Chandraprakash Mishra')
        self.assertEqual(doc.extractedFields['fatherName'], 'Chandraprakash Mishra')

        app.refresh_from_db()
        self.assertEqual(app.applicantName, 'Shivam Chandraprakash Mishra')
        self.assertEqual(app.identityDetails['panName'], 'Shivam Chandraprakash Mishra')
        self.assertEqual(app.identityDetails['fatherName'], 'Chandraprakash Mishra')
