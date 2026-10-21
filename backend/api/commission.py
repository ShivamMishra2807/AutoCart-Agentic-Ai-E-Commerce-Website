"""
AutoCart's seller fees, in one place so the website, the dashboard and the payout maths always agree.

Business model (modelled on how large marketplaces such as Amazon and Flipkart earn):
the seller pays nothing to join or list. AutoCart takes a commission only when something sells, and the rate depends on the category.
These are PROPOSED launch rates for this project, not a signed price list; they are easy to change here.
"""

RATES = {  # percent of the item price (before delivery)
    'Electronics': 5, 'Fashion': 10, 'Home & Kitchen': 8, 'Beauty & Personal Care': 8, 'Sports & Fitness': 7,
    'Books & Stationery': 4, 'Grocery & Gourmet': 3, 'Toys & Baby Care': 7,
}
DEFAULT_RATE = 6
PAYMENT_FEE_PERCENT = 2  # online payments only: the payment gateway's own charge, passed through at cost (Razorpay's standard rate)


def rate_for(category):
    return RATES.get(category, DEFAULT_RATE)


def fee_for(category, amount):
    return round(float(amount) * rate_for(category) / 100, 2)


def public_terms():
    return {
        'joiningFee': 0, 'listingFee': 0, 'monthlyFee': 0, 'paymentFeePercent': PAYMENT_FEE_PERCENT, 'defaultRate': DEFAULT_RATE,
        'rates': [{'category': c, 'percent': r} for c, r in sorted(RATES.items(), key=lambda x: x[1])],
        'note': 'Proposed launch rates. You only pay when you sell. You will see the exact terms before you accept them.',
    }


from rest_framework.decorators import api_view, permission_classes  # noqa: E402
from rest_framework.permissions import AllowAny  # noqa: E402
from rest_framework.response import Response  # noqa: E402


@api_view(['GET'])
@permission_classes([AllowAny])
def commission_view(request):
    """Public: sellers (and curious sellers-to-be) can see exactly what AutoCart charges."""
    return Response(public_terms())
