"""
Tests for Indian PIN Code Resolution & Residential City Auto-fill (Part H).

Verifies:
1. Valid 6-digit Indian PIN code queries postal lookup service and resolves city, district, state.
2. Separation of city and district (e.g. PIN 421301: city Kalyan, district Thane).
3. Ambiguity handling and address context disambiguation.
4. Invalid PIN code rejection (400 / 404) without crashing.
5. Integration with Aadhaar OCR extraction: auto-populating residentialCity, residentialState, residentialPincode.
6. Persistence in SellerApplication without overwriting commercial store address.
"""

from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from api.location_service import lookup_pincode_details
from api.seller_docs import parse_aadhaar
from api.models import SellerApplication

User = get_user_model()


class PincodeLookupServiceTests(TestCase):
    def test_valid_pincode_akola_444001(self):
        """PIN 444001 should resolve to Akola, Maharashtra."""
        res = lookup_pincode_details('444001')
        self.assertIsNotNone(res)
        self.assertEqual(res['state'], 'Maharashtra')
        self.assertIn('Akola', res['district'])
        self.assertIn('Akola', res['city'])
        self.assertTrue(len(res['localities']) > 0)

    def test_city_district_separation_kalyan_421301(self):
        """
        PIN 421301 has District 'Thane', but City/Taluk 'Kalyan'.
        The system must NOT blindly equate district to city.
        """
        res = lookup_pincode_details('421301')
        self.assertIsNotNone(res)
        self.assertEqual(res['state'], 'Maharashtra')
        self.assertEqual(res['district'], 'Thane')
        self.assertEqual(res['city'], 'Kalyan')

    def test_address_context_disambiguation(self):
        """
        Address context mentioning a specific locality or office
        resolves matched city and clears ambiguity flag.
        """
        addr = "Flat 402, Building 3, Mharal Pada, Kalyan West, Maharashtra"
        res = lookup_pincode_details('421301', address_context=addr)
        self.assertIsNotNone(res)
        self.assertEqual(res['city'], 'Kalyan')
        self.assertFalse(res['isAmbiguous'])

    def test_invalid_pincode_format(self):
        """Invalid formats (alphabetic, <6 digits, starting with 0) must return None."""
        self.assertIsNone(lookup_pincode_details('12345'))
        self.assertIsNone(lookup_pincode_details('012345'))
        self.assertIsNone(lookup_pincode_details('abcdef'))
        self.assertIsNone(lookup_pincode_details(''))
        self.assertIsNone(lookup_pincode_details(None))

    def test_nonexistent_pincode(self):
        """A 6-digit PIN code that does not exist in postal records should return None."""
        res = lookup_pincode_details('999999')
        self.assertIsNone(res)


class PincodeLookupAPITests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_api_valid_pincode(self):
        resp = self.client.get('/api/location/pincode-lookup?pincode=444001')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['pincode'], '444001')
        self.assertIn('Akola', data['district'])
        self.assertEqual(data['state'], 'Maharashtra')
        self.assertIn('city', data)

    def test_api_invalid_pincode(self):
        resp = self.client.get('/api/location/pincode-lookup?pincode=123')
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(resp.json().get('valid', True))
        self.assertIn('detail', resp.json())

    def test_api_with_address_context(self):
        resp = self.client.get('/api/location/pincode-lookup?pincode=421301&address=Kalyan+West')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['city'], 'Kalyan')
        self.assertEqual(data['district'], 'Thane')


class AadhaarOCRPincodeIntegrationTests(TestCase):
    def test_aadhaar_ocr_populates_residential_city_and_state(self):
        """
        When Aadhaar OCR extracts address and 444001 PIN,
        residentialCity and residentialState are automatically resolved.
        """
        text = """
Government of India
Ashwin Anand Agrawal
DOB: 30/12/2005
Address:
S/O Anand Agrawal, Khirwal Kutti, Near Honda Showroom, Alsi Plot,
Akola, Maharashtra - 444001
XXXX XXXX 9974
"""
        parsed = parse_aadhaar(text)
        self.assertEqual(parsed['name'], 'Ashwin Anand Agrawal')
        self.assertEqual(parsed['residentialPincode'], '444001')
        self.assertEqual(parsed['residentialCity'], 'Akola')
        self.assertEqual(parsed['residentialState'], 'Maharashtra')
        self.assertEqual(parsed['residentialDistrict'], 'Akola')
        self.assertIn('residentialCity', parsed['fieldConfidences'])


class SellerApplicationPersistenceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='seller_part_h@autocart.com',
            name='Test Seller',
            password='TestPassword123!'
        )

    def test_save_preserves_residential_and_store_separation(self):
        """
        Verify that residentialCity, residentialPincode, residentialAddress
        are persisted and do not overwrite store address, city, and pincode.
        """
        app = SellerApplication.objects.create(
            id='app_test_part_h_1',
            ownerUserId=str(self.user.id),
            applicantName='Test Seller',
            companyName='HyperMart Store',
            email='seller_part_h@autocart.com',
            phone='9820012345',
            # Store commercial address
            address='Shop 12, Phoenix Marketcity, Kurla West',
            city='Mumbai',
            addressState='Maharashtra',
            pincode='400070',
            storeLatitude=19.0864,
            storeLongitude=72.8890,
            # Personal residential address
            residentialAddress='Flat 101, Shanti Sadan, Alsi Plot, Akola',
            residentialPincode='444001',
            residentialCity='Akola',
            residentialState='Maharashtra',
        )

        app.refresh_from_db()
        # Verify residential fields
        self.assertEqual(app.residentialCity, 'Akola')
        self.assertEqual(app.residentialPincode, '444001')
        self.assertEqual(app.residentialState, 'Maharashtra')
        self.assertIn('Alsi Plot', app.residentialAddress)

        # Verify commercial store fields were completely preserved
        self.assertEqual(app.city, 'Mumbai')
        self.assertEqual(app.pincode, '400070')
        self.assertEqual(app.addressState, 'Maharashtra')
        self.assertIn('Phoenix Marketcity', app.address)
