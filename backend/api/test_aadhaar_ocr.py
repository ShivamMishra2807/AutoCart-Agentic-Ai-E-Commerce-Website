"""
Regression tests for Aadhaar Document OCR and layout extraction.
Verifies:
1. Name extraction extracts real English name adjacent to DOB, avoiding Devanagari gibberish.
2. Residential address strictly terminates before UIDAI disclaimer text and footers.
3. Residential address does not overwrite store commercial address.
4. Correct 6-digit Indian PIN code extraction.
5. Field-level confidence scores are calculated accurately.
6. Masked Aadhaar is validated and unmasked Aadhaar is rejected.
"""

from django.test import TestCase
from api.seller_docs import parse_aadhaar, process_document, _looks_like_name, _pretty_name
import os

class AadhaarOCRTestCase(TestCase):
    def test_looks_like_name(self):
        self.assertTrue(_looks_like_name("Ashwin Anand Agrawal"))
        self.assertTrue(_looks_like_name("Shivam Chandra Prakash Mishra"))
        self.assertTrue(_looks_like_name("Rahul Sharma"))
        # Header text, disclaimer words, numbers should fail
        self.assertFalse(_looks_like_name("Government of India"))
        self.assertFalse(_looks_like_name("Unique Identification Authority"))
        self.assertFalse(_looks_like_name("1947"))
        self.assertFalse(_looks_like_name("DOB: 12/05/1990"))
        self.assertFalse(_looks_like_name("Aadhaar is proof of identity"))

    def test_parse_aadhaar_mock_layout(self):
        text = """
Government of India
Unique Identification Authority of India
Ashwin Anand Agrawal
DOB: 30/12/2005
Male
Address:
S/O Anand Agrawal, Khirwal Kutti,
Near Honda Showroom, Alsi Plot,
Akola, Maharashtra - 444001
Aadhaar is proof of identity, not of citizenship.
1947 help@uidai.gov.in www.uidai.gov.in
XXXX XXXX 9974
VID: 9150668281440530
"""
        items = [
            {'text': 'Government of India', 'score': 0.86},
            {'text': 'Ashwin Anand Agrawal', 'score': 0.90},
            {'text': 'DOB: 30/12/2005', 'score': 0.85},
            {'text': 'Male', 'score': 0.80},
            {'text': 'Address:', 'score': 0.77},
            {'text': 'S/O Anand Agrawal, Khirwal Kutti,', 'score': 0.88},
            {'text': 'Near Honda Showroom, Alsi Plot,', 'score': 0.89},
            {'text': 'Akola, Maharashtra - 444001', 'score': 0.91},
            {'text': 'Aadhaar is proof of identity, not of citizenship.', 'score': 0.85},
            {'text': 'XXXX XXXX 9974', 'score': 0.87},
        ]
        parsed = parse_aadhaar(text, items=items)

        self.assertEqual(parsed['name'], 'Ashwin Anand Agrawal')
        self.assertEqual(parsed['dob'], '30/12/2005')
        self.assertEqual(parsed['gender'], 'Male')
        self.assertEqual(parsed['residentialPincode'], '444001')
        self.assertEqual(parsed['aadhaarLast4'], '9974')
        self.assertEqual(parsed['aadhaarMasked'], 'XXXX-XXXX-9974')

        # Store address must not be set from Aadhaar
        self.assertIsNone(parsed['address'])
        self.assertIsNone(parsed['pincode'])

        # Residential address must NOT contain UIDAI disclaimers
        self.assertIn('Khirwal Kutti', parsed['residentialAddress'])
        self.assertIn('444001', parsed['residentialAddress'])
        self.assertNotIn('citizenship', parsed['residentialAddress'])
        self.assertNotIn('proof of identity', parsed['residentialAddress'])
        self.assertNotIn('1947', parsed['residentialAddress'])

        # Field confidences
        conf = parsed['fieldConfidences']
        self.assertGreaterEqual(conf['name'], 85.0)
        self.assertGreaterEqual(conf['dob'], 80.0)
        self.assertGreaterEqual(conf['residentialPincode'], 85.0)

    def test_unmasked_aadhaar_rejected(self):
        # Full 12 digits visible without masking
        unmasked_text = "Government of India\nJohn Doe\nDOB: 01/01/1990\n1234 5678 9012"
        res = parse_aadhaar(unmasked_text)
        self.assertTrue(res.get('unmasked'))
