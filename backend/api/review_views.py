"""
Customer reviews.

- Anyone can read them. Only signed-in customers can write one, and each person gets one review per product.
- "Verified buyer" is earned: the person must have a non-cancelled order that contains the product.
- Reviewer names are shown as first name and last initial. Emails are never shown.
"""

from rest_framework import status as http
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Order, Product, Review
from .views import get_user_from_token


def _display_name(name: str) -> str:
    parts = (name or '').split()
    if not parts:
        return 'A customer'
    return parts[0] if len(parts) == 1 else f'{parts[0]} {parts[-1][0]}.'


def _row(r: Review):
    return {'id': r.id, 'name': _display_name(r.userName), 'rating': r.rating, 'title': r.title, 'body': r.body,
            'verified': r.verified, 'createdAt': r.createdAt}


def _bought(user, product_id: str) -> bool:
    for order in Order.objects.filter(customerEmail__iexact=user.email).exclude(status='Cancelled'):
        if any(str(i.get('id')) == product_id for i in (order.items or [])):
            return True
    return False


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def reviews_view(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    if not product:
        return Response({'detail': 'Product not found.'}, status=http.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        rows = list(Review.objects.filter(productId=product_id))
        dist = {str(n): sum(1 for r in rows if r.rating == n) for n in range(5, 0, -1)}
        avg = round(sum(r.rating for r in rows) / len(rows), 1) if rows else None
        user = get_user_from_token(request)
        mine = next((r for r in rows if user and r.userEmail.lower() == user.email.lower()), None)
        return Response({'count': len(rows), 'average': avg, 'distribution': dist, 'reviews': [_row(r) for r in rows[:50]],
                         'mine': _row(mine) if mine else None, 'canReview': bool(user), 'verifiedBuyer': bool(user and _bought(user, product_id))})

    user = get_user_from_token(request)
    if not user:
        return Response({'detail': 'Please sign in to write a review.'}, status=http.HTTP_401_UNAUTHORIZED)
    try:
        rating = int(request.data.get('rating'))
    except (TypeError, ValueError):
        rating = 0
    title = str(request.data.get('title') or '').strip()[:120]
    body = str(request.data.get('body') or '').strip()
    errors = {}
    if not 1 <= rating <= 5:
        errors['rating'] = 'Choose 1 to 5 stars.'
    if len(body) < 10:
        errors['body'] = 'Tell others a little more (at least 10 characters).'
    if len(body) > 1500:
        errors['body'] = 'Please keep it under 1500 characters.'
    if errors:
        return Response({'detail': 'Please fix the highlighted fields.', 'errors': errors}, status=http.HTTP_400_BAD_REQUEST)

    review, created = Review.objects.update_or_create(
        productId=product_id, userEmail=user.email.lower(),
        defaults={'userName': user.name, 'rating': rating, 'title': title, 'body': body, 'verified': _bought(user, product_id)},
    )
    return Response(_row(review), status=http.HTTP_201_CREATED if created else http.HTTP_200_OK)
