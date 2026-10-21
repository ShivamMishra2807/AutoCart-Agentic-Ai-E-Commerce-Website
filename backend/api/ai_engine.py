"""
AutoCart AI Engine Compatibility Layer.
Re-routes calls to the new multi-agent engine while preserving existing helper signatures.
"""

from .agents import agent_engine, SessionMemoryManager, GeminiProvider, LLMConfig
from .agents.tools import (
    search_products,
    get_product_details,
    compare_products,
    filter_products_by_budget,
    check_product_availability,
    get_my_orders,
    get_my_order_details,
    get_cart_summary,
    get_shipping_policy,
    get_return_policy,
    validate_seller_application,
    get_pending_seller_applications,
    get_seller_application_status,
    summarize_seller_application,
    product_to_dict as product_dict,
)


def search_catalog(query, limit=6):
    res = search_products(query=query, limit=limit)
    from .models import Product
    ids = [p['id'] for p in res.get('products', [])]
    return list(Product.objects.filter(id__in=ids))


def compare_catalog(product_ids):
    res = compare_products(product_ids)
    return res.get('comparison', [])


def customer_context(email):
    res = get_my_orders(customer_email=email, limit=5)
    return {'orders': res.get('orders', [])}


def discovery_agent(prompt, customer=None, session_id=None):
    email = customer.get('email') if isinstance(customer, dict) else None
    return agent_engine.run_discovery_agent(query=prompt, session_id=session_id, customer_email=email)


def customer_engagement_agent(prompt, email='', cart_items=None, session_id=None):
    return agent_engine.run_customer_engagement_agent(
        query=prompt, customer_email=email, cart_items=cart_items, session_id=session_id
    )


def seller_onboarding_agent(data, user_role='GUEST', user_email=''):
    return agent_engine.run_seller_onboarding_agent(
        application_data=data, user_role=user_role, user_email=user_email
    )
