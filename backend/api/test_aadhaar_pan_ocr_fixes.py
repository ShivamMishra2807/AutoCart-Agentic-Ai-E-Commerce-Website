import unittest
from api import seller_docs
from api.seller_views import _doc_json
from unittest.mock import MagicMock


class AadhaarPanOcrFixesTestCase(unittest.TestCase):
    def test_looks_like_name_rejects_garbage_and_signature_tokens(self):
        """Rejects consonant acronyms, signature words, and headers."""
        self.assertFalse(seller_docs._looks_like_name("HRR"))
        self.assertFalse(seller_docs._looks_like_name("NSDL"))
        self.assertFalse(seller_docs._looks_like_name("UTITSL"))
        self.assertFalse(seller_docs._looks_like_name("Verified"))
        self.assertFalse(seller_docs._looks_like_name("Signature Not Verified"))
        self.assertFalse(seller_docs._looks_like_name("INCOME TAX DEPARTMENT"))
        self.assertFalse(seller_docs._looks_like_name("12082024"))

        # Valid names with vowels should pass
        self.assertTrue(seller_docs._looks_like_name("Shivam Chandraprakash Mishra"))
        self.assertTrue(seller_docs._looks_like_name("Anand Agrawal"))
        self.assertTrue(seller_docs._looks_like_name("Rahul Sharma"))

    def test_pan_bounded_extraction_ignores_signature_and_hrr(self):
        """Tests that text outside the identity band (HRR, Verified) is strictly excluded."""
        ocr_text = """
        HRR
        INCOMETAXDEPARTMENT GOVT.OFINDIA
        e-PermanentAccountNumber(e-PAN)Card
        KBCPM8395F
        /Name SHIVAMCHANDRAPRAKASHMISHRA
        fa/Father'sname CHANDRAPRAKASHMISHRA
        /DateofBirth 05/06/2007
        /Gender Male
        Signature Not
        Verified
        IncomeTaxDept
        Date:2025.09 220
        """
        items = [
            {'text': 'KBCPM8395F', 'score': 0.94},
            {'text': 'SHIVAMCHANDRAPRAKASHMISHRA', 'score': 0.88},
            {'text': 'CHANDRAPRAKASHMISHRA', 'score': 0.87},
            {'text': '05/06/2007', 'score': 0.92},
        ]
        parsed = seller_docs.parse_pan(ocr_text, items=items)
        self.assertEqual(parsed['pan'], 'KBCPM8395F')
        self.assertIn("Shivam", parsed['name'])
        self.assertIn("Mishra", parsed['name'])
        self.assertNotIn("Hrr", parsed['name'])
        self.assertIn("Chandra", parsed['fatherName'])
        self.assertIn("Mishra", parsed['fatherName'])
        self.assertNotIn("Verified", parsed['fatherName'])
        self.assertEqual(parsed['dob'], '05/06/2007')

        # Genuine confidences
        self.assertIn('fieldConfidences', parsed)
        fc = parsed['fieldConfidences']
        self.assertEqual(fc['pan'], 94.0)
        self.assertGreater(fc['name'], 80.0)
        self.assertGreater(fc['fatherName'], 80.0)
        self.assertEqual(fc['dob'], 92.0)

    def test_pan_preserves_word_spacing(self):
        """Preserves spaces in composite names across different cards without hardcoding."""
        n1, f1, amb1 = seller_docs._split_glued_pan_names(
            'ASHWINANANDAGRAWAL', 'ANANDNANDKISHORAGRAWAL'
        )
        self.assertEqual(n1, 'Ashwin Anand Agrawal')
        self.assertEqual(f1, 'Anand Nandkishor Agrawal')
        self.assertFalse(amb1)

    def test_aadhaar_address_strips_sw_male_and_e_prefix(self):
        """Tests removing 'SW/ MALE Address:' and cleaning 'EMaharashtra'."""
        text = """
        Goyemmentofindia Unique Identification Authority of india
        Shivam Chandra Prakash Mishra e/DOB:05/06/2007
        SW/ MALE Address:
        352,mharalpada,murbad road,kalyan., Mharal
        Bk, PO: Varap, DIST: Thane,
        EMaharashtra - 421301
        Aadhaar is proof of identity, not of citizenship
        """
        items = [
            {'text': 'Shivam Chandra Prakash Mishra', 'score': 0.92},
            {'text': '05/06/2007', 'score': 0.88},
            {'text': '352,mharalpada,murbad road,kalyan.', 'score': 0.89},
            {'text': 'EMaharashtra - 421301', 'score': 0.86},
        ]
        parsed = seller_docs.parse_aadhaar(text, items=items)
        self.assertEqual(parsed['name'], 'Shivam Chandra Prakash Mishra')
        self.assertEqual(parsed['dob'], '05/06/2007')
        self.assertEqual(parsed['residentialPincode'], '421301')

        addr = parsed['residentialAddress']
        self.assertNotIn('SW/', addr)
        self.assertNotIn('MALE', addr)
        self.assertNotIn('Address:', addr)
        self.assertIn('352,mharalpada,murbad road,kalyan.', addr)
        self.assertIn('Maharashtra - 421301', addr)
        self.assertNotIn('EMaharashtra', addr)

    def test_doc_json_field_confidences_not_in_extracted_fields(self):
        """Ensures fieldConfidences is top-level and not in extractedFields to prevent [object Object]."""
        mock_doc = MagicMock()
        mock_doc.id = 'doc-123'
        mock_doc.docType = 'PAN'
        mock_doc.fileName = 'pan.jpg'
        mock_doc.mimeType = 'image/jpeg'
        mock_doc.sizeBytes = 1024
        mock_doc.ocrStatus = 'DONE'
        mock_doc.confidence = 88.5
        mock_doc.warnings = []
        mock_doc.uploadedAt = '2026-10-21T10:00:00Z'
        mock_doc.application_id = 'app-123'
        mock_doc.redactedText = 'Sample text'
        mock_doc.extractedFields = {
            'pan': 'ABCDE1234F',
            'name': 'Rahul Sharma',
            'fieldConfidences': {'pan': 95.0, 'name': 82.0}
        }

        res = _doc_json(mock_doc, admin=False)
        self.assertEqual(res['fieldConfidences'], {'pan': 95.0, 'name': 82.0})
        self.assertNotIn('fieldConfidences', res['extractedFields'])
        self.assertEqual(res['extractedFields']['name'], 'Rahul Sharma')


if __name__ == '__main__':
    unittest.main()
