from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import (
    login_view,
    register_view,
    me_view,
    ProductViewSet,
    CategoryViewSet,
    CouponViewSet,
    apply_coupon_view,
    OrderViewSet,
    admin_stats_view,
    admin_analytics_view,
    SellerViewSet,
    UserViewSet,
    ai_shopping_assistant_view,
    ai_discovery_view,
    ai_customer_engagement_view,
    ai_seller_onboarding_view,
    ai_recommendations_view,
    ai_compare_view,
    ai_seller_assistant_view,
    ai_admin_assistant_view,
    stores_nearby_view,
    store_zones_view,
    store_inventory_view,
    order_quote_view,
    order_reserve_stock_view,
    customer_address_view,
    )
from .support_views import (
    support_chat_view,
    support_chat_rating_view,
    support_tickets_view,
    support_ticket_detail_view,
    support_ticket_messages_view,
    support_summary_view,
)
from .order_views import (
    order_tracking_view, order_return_view, order_cancel_view,
)
from .commission import commission_view
from .assistant_memory import assistant_memory_view
from .support_views import support_last_address_view
from .seller_views import admin_seller_detail_view, seller_application_start_view, seller_application_product_image_view
from .product_images import serve_photo
from .role_views import seller_stock_log_view
from .upi_payments import upi_check_view, order_upi_view, order_upi_reference_view, payment_confirm_view, seller_payout_settings_view, payments_admin_view
from .seller_orders import seller_pack_order_view, seller_order_route_view
from .seller_assistant import seller_assistant_view
from .role_views import seller_product_create_view, seller_overview_view, seller_product_update_view, admin_overview_view, enquiry_draft_view
from .review_views import reviews_view
from .enquiry_views import enquiries_view, enquiry_answer_view, product_questions_view
from .catalog_views import catalog_summary_view, ai_status_view, health_view
from .seller_views import (
    seller_applications_view,
    seller_application_detail_view,
    seller_application_documents_view,
    seller_application_submit_view,
    seller_application_prepare_view,
    seller_document_file_view,
    admin_seller_application_action_view,
)
from .location_service import pincode_lookup_view, reverse_geocode_view, geocode_view

router_no_slash = DefaultRouter(trailing_slash=False)
router_slash = DefaultRouter(trailing_slash=True)

routes = [
    ('products', ProductViewSet, 'product'),
    ('categories', CategoryViewSet, 'category'),
    ('coupons', CouponViewSet, 'coupon'),
    ('orders', OrderViewSet, 'order'),
    ('sellers', SellerViewSet, 'seller'),
    ('users', UserViewSet, 'user'),
]

for prefix, viewset, basename in routes:
    router_no_slash.register(prefix, viewset, basename=basename)
    router_slash.register(prefix, viewset, basename=f"{basename}_slash")

urlpatterns = [
    # Auth
    re_path(r'^auth/login/?$', login_view, name='login'),
    re_path(r'^auth/register/?$', register_view, name='register'),
    re_path(r'^auth/me/?$', me_view, name='me'),
    re_path(r'^auth/address(?:es)?/?$', customer_address_view, name='customer_address'),

    # Coupons
    re_path(r'^coupons/apply/?$', apply_coupon_view, name='apply_coupon'),

    # Admin
    re_path(r'^admin/stats/?$', admin_stats_view, name='admin_stats'),
    re_path(r'^admin/analytics/?$', admin_analytics_view, name='admin_analytics'),

    # AI Agents Orchestrator Endpoints
    re_path(r'^ai/shopping-assistant/?$', ai_shopping_assistant_view, name='ai_shopping_assistant'),
    re_path(r'^ai/discovery/?$', ai_discovery_view, name='ai_discovery'),
    re_path(r'^ai/customer-engagement/?$', ai_customer_engagement_view, name='ai_customer_engagement'),
    re_path(r'^ai/seller-onboarding/?$', ai_seller_onboarding_view, name='ai_seller_onboarding'),
    re_path(r'^ai/seller-assistant/?$', ai_seller_assistant_view, name='ai_seller_assistant'),
    re_path(r'^ai/admin-assistant/?$', ai_admin_assistant_view, name='ai_admin_assistant'),
    re_path(r'^ai/recommendations/?$', ai_recommendations_view, name='ai_recommendations'),
    re_path(r'^ai/compare/?$', ai_compare_view, name='ai_compare'),

    # Public catalogue numbers + admin AI status
    re_path(r'^catalog/summary/?$', catalog_summary_view, name='catalog_summary'),
    re_path(r'^ai/status/?$', ai_status_view, name='ai_status'),
    re_path(r'^health/?$', health_view, name='health'),

    # Payments: UPI scan-and-pay, confirmed by the seller
    re_path(r'^payments/upi-check/?$', upi_check_view, name='upi_check'),
    re_path(r'^orders/(?P<order_id>[^/]+)/upi/?$', order_upi_view, name='order_upi'),
    re_path(r'^orders/(?P<order_id>[^/]+)/upi-reference/?$', order_upi_reference_view, name='order_upi_reference'),
    re_path(r'^orders/(?P<order_id>[^/]+)/payment/?$', payment_confirm_view, name='payment_confirm'),
    re_path(r'^seller/payout-settings/?$', seller_payout_settings_view, name='seller_payout_settings'),
    re_path(r'^payments/status/?$', payments_admin_view, name='payment_status'),

    # Role-specific views (each role only gets its own)
    re_path(r'^seller/overview/?$', seller_overview_view, name='seller_overview'),
    re_path(r'^seller/products/?$', seller_product_create_view, name='seller_product_create'),
    re_path(r'^commission/?$', commission_view, name='commission_terms'),
    re_path(r'^support/last-address/?$', support_last_address_view, name='support_last_address'),
    re_path(r'^support/memory/?$', assistant_memory_view, name='assistant_memory'),
    re_path(r'^seller/orders/(?P<order_id>[^/]+)/pack/?$', seller_pack_order_view, name='seller_pack_order'),
    re_path(r'^seller/orders/(?P<order_id>[^/]+)/route/?$', seller_order_route_view, name='seller_order_route'),
    re_path(r'^admin/sellers/(?P<seller_id>[^/]+)/detail/?$', admin_seller_detail_view, name='admin_seller_detail'),
    re_path(r'^media/product_images/(?P<name>[A-Za-z0-9._-]+)$', serve_photo, name='product_photo'),
    re_path(r'^seller/products/(?P<product_id>[^/]+)/stock-log/?$', seller_stock_log_view, name='seller_stock_log'),
    re_path(r'^seller/assistant/?$', seller_assistant_view, name='seller_assistant'),
    re_path(r'^seller/products/(?P<product_id>[^/]+)/?$', seller_product_update_view, name='seller_product_update'),
    re_path(r'^admin/overview/?$', admin_overview_view, name='admin_overview'),
    re_path(r'^enquiries/(?P<enquiry_id>[^/]+)/draft/?$', enquiry_draft_view, name='enquiry_draft'),

    # Reviews
    re_path(r'^reviews/(?P<product_id>[^/]+)/?$', reviews_view, name='reviews'),

    # Customer enquiries
    re_path(r'^enquiries/?$', enquiries_view, name='enquiries'),
    re_path(r'^enquiries/(?P<enquiry_id>[^/]+)/answer/?$', enquiry_answer_view, name='enquiry_answer'),
    re_path(r'^product-questions/(?P<product_id>[^/]+)/?$', product_questions_view, name='product_questions'),

    # Customer support: chat, tickets, human handoff
    re_path(r'^support/chat/?$', support_chat_view, name='support_chat'),
    re_path(r'^support/chat/(?P<session_id>[^/]+)/rating/?$', support_chat_rating_view, name='support_chat_rating'),
    re_path(r'^support/summary/?$', support_summary_view, name='support_summary'),
    re_path(r'^support/tickets/?$', support_tickets_view, name='support_tickets'),
    re_path(r'^support/tickets/(?P<ticket_id>[^/]+)/messages/?$', support_ticket_messages_view, name='support_ticket_messages'),
    re_path(r'^support/tickets/(?P<ticket_id>[^/]+)/?$', support_ticket_detail_view, name='support_ticket_detail'),

    # Nearby Physical Stores & Inventory
    re_path(r'^stores/nearby/?$', stores_nearby_view, name='stores_nearby'),
    re_path(r'^stores/zones/?$', store_zones_view, name='store_zones'),
    re_path(r'^stores/(?P<store_id>[^/]+)/inventory/?$', store_inventory_view, name='store_inventory'),
    re_path(r'^location/pincode-lookup/?$', pincode_lookup_view, name='pincode_lookup'),
    re_path(r'^location/reverse-geocode/?$', reverse_geocode_view, name='reverse_geocode'),
    re_path(r'^location/geocode/?$', geocode_view, name='location_geocode'),

    # Fulfillment Quotes & Atomic Inventory Reservations
    re_path(r'^orders/quote/?$', order_quote_view, name='order_quote'),
    re_path(r'^orders/reserve-stock/?$', order_reserve_stock_view, name='order_reserve_stock'),

    # Order Tracking, Returns & Cancellations
    re_path(r'^orders/(?P<order_id>[^/]+)/tracking/?$', order_tracking_view, name='order_tracking'),
    re_path(r'^orders/(?P<order_id>[^/]+)/return/?$', order_return_view, name='order_return'),
    re_path(r'^orders/(?P<order_id>[^/]+)/cancel/?$', order_cancel_view, name='order_cancel'),

    # Seller Applications & Admin Workflow
    re_path(r'^seller/applications/(?P<pk>[^/]+)/product-image/?$', seller_application_product_image_view, name='seller_application_product_image'),
    re_path(r'^seller/applications/start/?$', seller_application_start_view, name='seller_application_start'),
    re_path(r'^seller/applications/?$', seller_applications_view, name='seller_applications'),
    re_path(r'^seller/applications/(?P<pk>[^/]+)/documents/(?P<doc_id>[^/]+)/file/?$', seller_document_file_view, name='seller_document_file'),
    re_path(r'^seller/applications/(?P<pk>[^/]+)/documents/?$', seller_application_documents_view, name='seller_application_documents'),
    re_path(r'^seller/applications/(?P<pk>[^/]+)/prepare/?$', seller_application_prepare_view, name='seller_application_prepare'),
    re_path(r'^seller/applications/(?P<pk>[^/]+)/submit/?$', seller_application_submit_view, name='seller_application_submit'),
    re_path(r'^seller/applications/(?P<pk>[^/]+)/?$', seller_application_detail_view, name='seller_application_detail'),
    re_path(r'^admin/seller-applications/(?P<pk>[^/]+)/action/?$', admin_seller_application_action_view, name='admin_seller_application_action'),

    # Router endpoints (both with and without trailing slash)
    path('', include(router_no_slash.urls)),
    path('', include(router_slash.urls)),
]

