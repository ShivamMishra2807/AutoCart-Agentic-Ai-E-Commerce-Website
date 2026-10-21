import os
import sys
import django
from datetime import datetime, timezone, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocart_core.settings')
django.setup()

from api.models import Store, StoreInventory, Product, Seller, SellerApplication, SellerApplicationAudit

def seed_stores_and_inventory():
    print("Seeding Physical Stores...")
    stores_data = [
        {
            'id': 'store-blr-01',
            'name': 'AutoCart Tech & Lifestyle Hub — Indiranagar',
            'seller': 'Appario Retail',
            'sellerId': 'seller-2',
            'address': '100 Feet Road, HAL 2nd Stage, Indiranagar',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'pincode': '560038',
            'latitude': 12.9784,
            'longitude': 77.6408,
            'phone': '+91 80 4123 4567',
            'email': 'indiranagar@autocart.in',
            'operatingStatus': 'Open',
            'serviceCoverageRadiusKm': 15.0,
            'fulfillmentCapability': 'Pickup and Delivery',
            'openingHours': '9:00 AM - 10:00 PM',
            'rating': 4.8,
        },
        {
            'id': 'store-blr-02',
            'name': 'AutoCart Digital Express — Koramangala',
            'seller': 'Appario Retail',
            'sellerId': 'seller-2',
            'address': '80 Feet Road, 4th Block, Koramangala',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'pincode': '560034',
            'latitude': 12.9352,
            'longitude': 77.6245,
            'phone': '+91 80 4234 5678',
            'email': 'koramangala@autocart.in',
            'operatingStatus': 'Open',
            'serviceCoverageRadiusKm': 12.0,
            'fulfillmentCapability': 'Pickup and Delivery',
            'openingHours': '9:30 AM - 9:30 PM',
            'rating': 4.7,
        },
        {
            'id': 'store-blr-03',
            'name': 'AutoCart Mega Mart — Whitefield',
            'seller': 'Swift Logistics & Retailers',
            'sellerId': 'seller-6',
            'address': 'ITPL Main Road, Whitefield',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'pincode': '560066',
            'latitude': 12.9698,
            'longitude': 77.7500,
            'phone': '+91 80 4345 6789',
            'email': 'whitefield@autocart.in',
            'operatingStatus': 'Open',
            'serviceCoverageRadiusKm': 20.0,
            'fulfillmentCapability': 'Pickup and Delivery',
            'openingHours': '10:00 AM - 10:00 PM',
            'rating': 4.6,
        },
        {
            'id': 'store-mum-01',
            'name': 'AutoCart Flagship Store — Bandra West',
            'seller': 'boAt Official Store',
            'sellerId': 'seller-1',
            'address': 'Hill Road, Near Bandra Station, Bandra West',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400050',
            'latitude': 19.0596,
            'longitude': 72.8295,
            'phone': '+91 22 2640 1122',
            'email': 'bandra@autocart.in',
            'operatingStatus': 'Open',
            'serviceCoverageRadiusKm': 15.0,
            'fulfillmentCapability': 'Pickup and Delivery',
            'openingHours': '10:00 AM - 10:00 PM',
            'rating': 4.9,
        },
        {
            'id': 'store-mum-02',
            'name': 'AutoCart Express — Andheri East',
            'seller': 'Swift Logistics & Retailers',
            'sellerId': 'seller-6',
            'address': 'Chakala, Andheri-Kurla Road, Andheri East',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400069',
            'latitude': 19.1136,
            'longitude': 72.8697,
            'phone': '+91 22 2820 3344',
            'email': 'andheri@autocart.in',
            'operatingStatus': 'Open',
            'serviceCoverageRadiusKm': 16.0,
            'fulfillmentCapability': 'Pickup and Delivery',
            'openingHours': '9:00 AM - 9:00 PM',
            'rating': 4.5,
        },
        {
            'id': 'store-del-01',
            'name': 'AutoCart Central Prime — Connaught Place',
            'seller': 'Biba Apparels',
            'sellerId': 'seller-3',
            'address': 'Radial Road 4, Inner Circle, Connaught Place',
            'city': 'New Delhi',
            'state': 'Delhi',
            'pincode': '110001',
            'latitude': 28.6304,
            'longitude': 77.2177,
            'phone': '+91 11 2341 5566',
            'email': 'cp.delhi@autocart.in',
            'operatingStatus': 'Open',
            'serviceCoverageRadiusKm': 18.0,
            'fulfillmentCapability': 'Pickup and Delivery',
            'openingHours': '10:00 AM - 9:00 PM',
            'rating': 4.8,
        },
        {
            'id': 'store-del-02',
            'name': 'AutoCart Lifestyle Hub — South Extension',
            'seller': 'Biba Apparels',
            'sellerId': 'seller-3',
            'address': 'South Extension Part II, Ring Road',
            'city': 'New Delhi',
            'state': 'Delhi',
            'pincode': '110049',
            'latitude': 28.5708,
            'longitude': 77.2215,
            'phone': '+91 11 2625 7788',
            'email': 'southex@autocart.in',
            'operatingStatus': 'Open',
            'serviceCoverageRadiusKm': 14.0,
            'fulfillmentCapability': 'Pickup and Delivery',
            'openingHours': '10:30 AM - 9:30 PM',
            'rating': 4.7,
        },
        {
            'id': 'store-hyd-01',
            'name': 'AutoCart Smart Hub — Hitec City',
            'seller': 'Appario Retail',
            'sellerId': 'seller-2',
            'address': 'Madhapur Main Road, Near Cyber Towers, Hitec City',
            'city': 'Hyderabad',
            'state': 'Telangana',
            'pincode': '500081',
            'latitude': 17.4474,
            'longitude': 78.3762,
            'phone': '+91 40 4567 8901',
            'email': 'hiteccity@autocart.in',
            'operatingStatus': 'Open',
            'serviceCoverageRadiusKm': 16.0,
            'fulfillmentCapability': 'Pickup and Delivery',
            'openingHours': '9:00 AM - 10:00 PM',
            'rating': 4.8,
        }
    ]

    for item in stores_data:
        Store.objects.update_or_create(id=item['id'], defaults=item)
    print(f"Total Stores in database: {Store.objects.count()}")

    print("Seeding Store Inventory for Products...")
    stores = list(Store.objects.all())
    products = list(Product.objects.all())

    inventory_count = 0
    for product in products:
        # Distribute inventory across stores with realistic quantities
        for i, store in enumerate(stores):
            # Deterministic variation based on store index
            qty = max(2, (int(product.stock) // len(stores)) + (i % 5) * 2)
            store_price = float(product.price)
            
            StoreInventory.objects.update_or_create(
                store=store,
                product=product,
                defaults={
                    'id': f"inv-{store.id}-{product.id}",
                    'availableQuantity': qty,
                    'reservedQuantity': 0,
                    'storePrice': store_price,
                    'isAvailable': qty > 0,
                }
            )
            inventory_count += 1

    print(f"Total Store Inventory mappings created: {inventory_count}")

    print("Seeding Multi-State Seller Applications...")
    now = datetime.now(timezone.utc)
    apps_data = [
        {
            'id': 'app-2026-001',
            'applicantName': 'Aarav Sharma',
            'companyName': 'Sharma Electronics Retail LLP',
            'email': 'aarav@sharmaelectronics.in',
            'phone': '9811223344',
            'city': 'Bengaluru',
            'address': 'Brigade Road, Ashok Nagar, Bengaluru',
            'pincode': '560025',
            'businessType': 'Retailer',
            'productCategories': ['Electronics', 'Home & Kitchen'],
            'gstin': '29ABCDE1234F1Z5',
            'pan': 'ABCDE1234F',
            'yearsInBusiness': '4',
            'status': 'PENDING_ADMIN_APPROVAL',
            'riskScore': 15,
            'riskCategory': 'Low',
            'documentUploads': {
                'gst_certificate': {'fileName': 'GST_Reg_Certificate.pdf', 'status': 'UPLOADED', 'verified': True},
                'pan_card': {'fileName': 'Proprietor_PAN.jpg', 'status': 'UPLOADED', 'verified': True},
                'trade_license': {'fileName': 'Trade_License_2026.pdf', 'status': 'UPLOADED', 'verified': True}
            },
            'ocrExtractedData': {
                'gstin': '29ABCDE1234F1Z5',
                'pan': 'ABCDE1234F',
                'extractedName': 'Aarav Sharma',
                'legalEntity': 'Sharma Electronics Retail LLP',
                'confidence': 96.5,
                'matchedFields': ['gstin', 'pan', 'applicantName', 'companyName']
            },
            'verificationResults': {
                'gstinStatus': 'ACTIVE',
                'taxCompliance': 'Compliant',
                'identityProof': 'Verified',
                'bankProof': 'Verified'
            },
            'missingFields': [],
            'aiAssessment': 'Agent D Assessment: Clean documentation. GSTIN state code (29) matches Karnataka operating address. High OCR confidence score (96.5%). Recommended for routine administrative approval.',
            'adminNotes': 'All three mandatory identity, tax, and trade documents verified.',
        },
        {
            'id': 'app-2026-002',
            'applicantName': 'Kavita Verma',
            'companyName': 'Verma Organics India',
            'email': 'kavita@vermaorganics.in',
            'phone': '9876543210',
            'city': 'Bengaluru',
            'address': 'Indiranagar 100ft Road, Bengaluru',
            'pincode': '560038',
            'businessType': 'Brand',
            'productCategories': ['Beauty & Personal Care', 'Grocery'],
            'gstin': '29VERMA5678G2Z9',
            'pan': 'VERMA5678G',
            'yearsInBusiness': '3',
            'status': 'APPROVED',
            'riskScore': 10,
            'riskCategory': 'Low',
            'documentUploads': {
                'gst_certificate': {'fileName': 'Verma_GST_Reg.pdf', 'status': 'VERIFIED', 'verified': True},
                'pan_card': {'fileName': 'Verma_PAN.jpg', 'status': 'VERIFIED', 'verified': True}
            },
            'ocrExtractedData': {
                'gstin': '29VERMA5678G2Z9',
                'pan': 'VERMA5678G',
                'extractedName': 'Kavita Verma',
                'legalEntity': 'Verma Organics India Pvt Ltd',
                'confidence': 98.2
            },
            'verificationResults': {
                'gstinStatus': 'ACTIVE',
                'identityProof': 'Verified'
            },
            'missingFields': [],
            'aiAssessment': 'Agent D Assessment: Fast-track approved. Organic trade certifications in place.',
            'reviewedBy': 'Administrator User',
        },
        {
            'id': 'app-2026-003',
            'applicantName': 'Unknown Representative',
            'companyName': 'Direct Import Hub',
            'email': 'temp_hub88@mailcatch.xyz',
            'phone': '9000000000',
            'city': 'Shenzhen / Offshore',
            'address': 'Offshore Free Trade Hub',
            'pincode': '000000',
            'businessType': 'Individual Seller',
            'productCategories': ['Electronics'],
            'gstin': '',
            'pan': '',
            'yearsInBusiness': '0',
            'status': 'NEEDS_MANUAL_REVIEW',
            'riskScore': 92,
            'riskCategory': 'High',
            'documentUploads': {
                'pan_card': {'fileName': 'blurry_id_scan.jpg', 'status': 'REJECTED_OCR_UNREADABLE', 'verified': False}
            },
            'ocrExtractedData': {
                'error': 'Low OCR contrast / unreadable text',
                'confidence': 24.0,
                'extractedCharacters': 'XX-990-???'
            },
            'verificationResults': {
                'gstinStatus': 'MISSING',
                'domainRisk': 'Disposable email provider (mailcatch.xyz) detected',
                'addressRisk': 'No physical address in domestic jurisdiction'
            },
            'missingFields': ['gstin', 'pan', 'valid_company_registration', 'domestic_address'],
            'aiAssessment': 'Agent D High-Risk Alert: Disposable domain email, repetitive phone number, unreadable uploaded ID, and no Indian GSTIN. Application must NOT be approved without physical KYC and domestic tax entity registration.',
            'adminNotes': 'Flagged for compliance investigation.',
        },
        {
            'id': 'app-2026-004',
            'applicantName': 'Rohan Das',
            'companyName': 'FastTrack Wholesale Mobiles',
            'email': 'contact@fasttrackmobiles.in',
            'phone': '9844221100',
            'city': 'Hyderabad',
            'address': 'Madhapur Hitec City, Hyderabad',
            'pincode': '500081',
            'businessType': 'Retailer',
            'productCategories': ['Electronics'],
            'gstin': '36DASRK9876H1Z1',
            'pan': 'DASRK9876H',
            'yearsInBusiness': '2',
            'status': 'NEEDS_MORE_INFORMATION',
            'riskScore': 45,
            'riskCategory': 'Medium',
            'documentUploads': {
                'gst_certificate': {'fileName': 'GST_Certificate_2025.pdf', 'status': 'UPLOADED', 'verified': True}
            },
            'ocrExtractedData': {
                'gstin': '36DASRK9876H1Z1',
                'confidence': 91.0
            },
            'verificationResults': {
                'gstinStatus': 'ACTIVE',
                'bankProof': 'PENDING_UPLOAD'
            },
            'missingFields': ['cancelled_cheque_or_bank_statement'],
            'aiAssessment': 'Agent D Assessment: GSTIN active for Telangana. Commercial bank account verification document missing. Requesting cancelled cheque / bank mandate before administrative review.',
            'adminNotes': 'Waiting for bank mandate from seller.',
        },
        {
            'id': 'app-2026-005',
            'applicantName': 'Vikram Mehra',
            'companyName': 'Mehra Handicrafts & Decor',
            'email': 'vikram@mehrahandicrafts.com',
            'phone': '9810334455',
            'city': 'Jaipur',
            'address': 'MI Road, Jaipur, Rajasthan',
            'pincode': '302001',
            'businessType': 'Manufacturer',
            'productCategories': ['Home & Kitchen', 'Fashion'],
            'gstin': '08MEHRA1234K1Z0',
            'pan': 'MEHRA1234K',
            'yearsInBusiness': '6',
            'status': 'DOCUMENT_PROCESSING',
            'riskScore': 25,
            'riskCategory': 'Low',
            'documentUploads': {
                'gst_certificate': {'fileName': 'Jaipur_GST_Certificate.pdf', 'status': 'PROCESSING', 'verified': False},
                'pan_card': {'fileName': 'Vikram_PAN.jpg', 'status': 'PROCESSING', 'verified': False}
            },
            'ocrExtractedData': {},
            'verificationResults': {},
            'missingFields': [],
            'aiAssessment': 'Agent D Assessment: New submission queued for automated document OCR extraction and tax verification.',
        }
    ]

    for app in apps_data:
        obj, created = SellerApplication.objects.update_or_create(id=app['id'], defaults=app)
        # Create initial audit log
        SellerApplicationAudit.objects.get_or_create(
            id=f"audit-{app['id']}-01",
            application=obj,
            defaults={
                'fromStatus': 'DRAFT',
                'toStatus': app['status'],
                'action': 'APPLICATION_SUBMITTED' if app['status'] != 'APPROVED' else 'ADMIN_APPROVED',
                'performedBy': 'Seller Applicant' if app['status'] != 'APPROVED' else 'Administrator User',
                'reason': app.get('adminNotes') or 'Application submitted for marketplace review'
            }
        )

    print(f"Total Seller Applications in database: {SellerApplication.objects.count()}")
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_stores_and_inventory()
