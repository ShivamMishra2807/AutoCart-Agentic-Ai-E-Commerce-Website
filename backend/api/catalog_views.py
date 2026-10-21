"""Public, read-only catalogue numbers (no private data) and an admin check for the AI provider."""

from django.core.cache import cache
from django.db.models import Avg, Count, Max, Min
from django.utils import timezone
from rest_framework import status as http
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Category, Product, Store
from .views import get_user_from_token

CACHE_KEY = 'catalog_summary_v1'


def build_catalog_summary() -> dict:
    products = Product.objects.all()
    agg = products.aggregate(lo=Min('price'), hi=Max('price'), rating=Avg('rating'))
    per_category = products.values('category').annotate(n=Count('id')).order_by('-n')
    stores = Store.objects.filter(operatingStatus='Open')
    return {
        'totalProducts': products.count(),
        'totalCategories': Category.objects.filter(status='Active').count(),
        'totalBrands': products.exclude(brand='').values('brand').distinct().count(),
        'totalStores': stores.count(),
        'totalCities': stores.values('city').distinct().count(),
        'inStock': products.filter(stock__gt=0).count(),
        'priceMin': agg['lo'] or 0,
        'priceMax': agg['hi'] or 0,
        'averageRating': round(agg['rating'] or 0, 2),
        'byCategory': [{'name': r['category'], 'count': r['n']} for r in per_category],
        'updatedAt': timezone.now().isoformat(),
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def catalog_summary_view(request):
    """Real totals straight from the database, cached for 5 minutes. Safe for anyone to see."""
    data = cache.get(CACHE_KEY)
    if data is None:
        data = build_catalog_summary()
        cache.set(CACHE_KEY, data, 300)
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def ai_status_view(request):
    """Admin only: which AI provider is set up. Never returns a key."""
    user = get_user_from_token(request)
    if not user or user.role not in ('ADMIN', 'STAFF'):
        return Response({'detail': 'Only an administrator can see this.'}, status=http.HTTP_403_FORBIDDEN)
    from .agents.llm_provider import LLMConfig, UnifiedLLMProvider
    provider = UnifiedLLMProvider()
    return Response({
        'active': provider.active_provider_name,
        'groqConfigured': provider.groq.is_configured,
        'geminiConfigured': provider.gemini.is_configured,
        'geminiModel': LLMConfig.get_gemini_model(),
        'fallback': 'Built-in rule-based engine answers when no AI provider is available.',
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_view(request):
    """For monitors and Docker: is the app up and can it reach its database?"""
    from django.db import connection
    try:
        with connection.cursor() as cur:
            cur.execute('SELECT 1')
        return Response({'status': 'ok', 'database': 'ok'})
    except Exception:
        return Response({'status': 'degraded', 'database': 'unreachable'}, status=http.HTTP_503_SERVICE_UNAVAILABLE)
