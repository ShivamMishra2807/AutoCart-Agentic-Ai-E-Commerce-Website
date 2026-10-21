import os
import sys
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocart_core.settings')
django.setup()

from api.models import User, Category, Product, Coupon, Seller, Order

def run_seed():
    with open('seed_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Seeding Categories...")
    for item in data.get('categories', []):
        Category.objects.update_or_create(
            id=item['id'],
            defaults={
                'name': item['name'],
                'slug': item['slug'],
                'icon': item.get('icon', ''),
                'image': item.get('image', ''),
                'description': item.get('description', ''),
                'productCount': item.get('productCount', 0),
                'status': item.get('status', 'Active'),
            }
        )

    print("Seeding Products...")
    for item in data.get('products', []):
        Product.objects.update_or_create(
            id=item['id'],
            defaults={
                'name': item['name'],
                'slug': item['slug'],
                'category': item['category'],
                'categoryId': item.get('categoryId', ''),
                'brand': item.get('brand', ''),
                'price': float(item.get('price', 0)),
                'originalPrice': float(item.get('originalPrice', 0)),
                'discount': int(item.get('discount', 0)),
                'rating': float(item.get('rating', 0)),
                'reviewCount': int(item.get('reviewCount', 0)),
                'stock': int(item.get('stock', 0)),
                'stockStatus': item.get('stockStatus', 'In Stock'),
                'featured': bool(item.get('featured', False)),
                'bestSeller': bool(item.get('bestSeller', False)),
                'newArrival': bool(item.get('newArrival', False)),
                'images': item.get('images', []),
                'description': item.get('description', ''),
                'specifications': item.get('specifications', {}),
                'seller': item.get('seller', ''),
                'createdAt': item.get('createdAt', ''),
            }
        )

    print("Seeding Coupons...")
    for item in data.get('coupons', []):
        Coupon.objects.update_or_create(
            id=item['id'],
            defaults={
                'code': item['code'],
                'discountType': item.get('discountType', 'Percentage'),
                'discountValue': float(item.get('discountValue', 0)),
                'minOrderAmount': float(item.get('minOrderAmount', 0)),
                'maxDiscount': float(item.get('maxDiscount', 0)),
                'startDate': item.get('startDate', ''),
                'expiryDate': item.get('expiryDate', ''),
                'usageLimit': int(item.get('usageLimit', 1000)),
                'usedCount': int(item.get('usedCount', 0)),
                'status': item.get('status', 'Active'),
                'description': item.get('description', ''),
            }
        )

    print("Seeding Sellers...")
    for item in data.get('sellers', []):
        Seller.objects.update_or_create(
            id=item['id'],
            defaults={
                'name': item['name'],
                'companyName': item.get('companyName', ''),
                'email': item.get('email', ''),
                'phone': item.get('phone', ''),
                'productsCount': int(item.get('productsCount', 0)),
                'ordersCount': int(item.get('ordersCount', 0)),
                'totalRevenue': float(item.get('totalRevenue', 0)),
                'rating': float(item.get('rating', 0)),
                'status': item.get('status', 'Approved'),
                'joinedDate': item.get('joinedDate', ''),
                'city': item.get('city', ''),
            }
        )

    print("Seeding Users...")
    for item in data.get('users', []):
        user, created = User.objects.update_or_create(
            id=item['id'],
            defaults={
                'name': item['name'],
                'email': item['email'].lower(),
                'phone': item.get('phone', ''),
                'role': item.get('role', 'CUSTOMER'),
                'status': item.get('status', 'Active'),
                'ordersCount': int(item.get('ordersCount', 0)),
                'totalSpent': float(item.get('totalSpent', 0)),
                'addresses': item.get('addresses', []),
                'is_staff': (item.get('role') == 'ADMIN'),
                'is_superuser': (item.get('role') == 'ADMIN'),
            }
        )
        # Demo accounts documented in the README: admin / admin123, everyone else / password
        user.set_password('admin123' if item.get('role') == 'ADMIN' else 'password')
        user.save()

    print("Seeding Orders...")
    for item in data.get('orders', []):
        Order.objects.update_or_create(
            id=item['id'],
            defaults={
                'customerName': item.get('customerName', ''),
                'customerEmail': item.get('customerEmail', ''),
                'customerPhone': item.get('customerPhone', ''),
                'date': item.get('date', ''),
                'totalAmount': float(item.get('totalAmount', 0)),
                'subtotal': float(item.get('subtotal', 0)),
                'tax': float(item.get('tax', 0)),
                'shippingFee': float(item.get('shippingFee', 0)),
                'discountAmount': float(item.get('discountAmount', 0)),
                'paymentMethod': item.get('paymentMethod', 'Cash on Delivery'),
                'paymentStatus': item.get('paymentStatus', 'Pending'),
                'status': item.get('status', 'Confirmed'),
                'shippingAddress': item.get('shippingAddress', {}),
                'items': item.get('items', []),
                'timeline': item.get('timeline', []),
            }
        )

    print("All seed data successfully loaded into Django database!")

if __name__ == '__main__':
    run_seed()
