"""
Creates one demo seller account so the seller sign-in page and the seller dashboard can be tried.

    python seed_demo_seller.py

Sign in at /seller/login with  seller@example.com / seller123
The seller is attached to the business that already sells the most products in the sample catalogue, so customer
questions about those products show up in this seller's dashboard. Safe to run more than once.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocart_core.settings')
django.setup()

from django.db.models import Count  # noqa: E402
from api.models import Product, Seller, SellerApplication, User  # noqa: E402

top = Product.objects.exclude(seller='').values('seller').annotate(n=Count('id')).order_by('-n').first()
company = top['seller'] if top else 'Demo Electronics'

user, _ = User.objects.update_or_create(
    email='seller@example.com',
    defaults={'id': 'user-demo-seller', 'name': 'Demo Seller', 'phone': '9820000001', 'role': 'SELLER', 'status': 'Active'},
)
user.set_password('seller123')
user.save()

SellerApplication.objects.update_or_create(
    id='app-demo-seller',
    defaults={
        'ownerUserId': user.id, 'applicantName': user.name, 'companyName': company, 'storeName': company, 'email': user.email,
        'phone': user.phone, 'city': 'Mumbai', 'address': 'Demo address, Andheri East', 'pincode': '400069', 'addressState': 'Maharashtra',
        'storeLatitude': 19.1136, 'storeLongitude': 72.8697, 'status': 'APPROVED', 'riskScore': 10, 'riskCategory': 'Low',
        'reviewedBy': 'seed', 'plannedProducts': [],
    },
)
Seller.objects.update_or_create(
    id='sel-app-demo-seller',
    defaults={'name': user.name, 'companyName': company, 'email': user.email, 'phone': user.phone, 'status': 'Approved', 'city': 'Mumbai'},
)
print(f"Demo seller ready: seller@example.com / seller123  (sells as '{company}', {Product.objects.filter(seller=company).count()} products)")
