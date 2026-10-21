"""
AutoCart LangChain Integration Module.
Implements LangChain primitives, LangChain Expression Language (LCEL) chains,
LangChain Tools (@tool), Document representations, Pydantic schemas,
and adapters for the AutoCart agent ecosystem.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.documents import Document
from langchain_core.tools import tool

from .agents.llm_provider import UnifiedLLMProvider

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. LangChain LLM Runnable Adapter
# ---------------------------------------------------------------------------

class LangChainLLMRunnable:
    """
    Adapts AutoCart's UnifiedLLMProvider into a first-class LangChain Runnable.
    Compatible with LangChain Expression Language (LCEL) pipelines:
        chain = prompt | LangChainLLMRunnable() | StrOutputParser()
    """

    def __init__(self, temperature: float = 0.3, max_tokens: int = 500):
        self.provider = UnifiedLLMProvider()
        self.temperature = temperature
        self.max_tokens = max_tokens

    def __call__(self, prompt_value: Any) -> str:
        return self.invoke(prompt_value)

    def invoke(self, input_val: Any, config: Optional[Dict[str, Any]] = None) -> str:
        system_text = ""
        user_text = ""

        # Extract system and user messages from LangChain ChatPromptValue or messages list
        if hasattr(input_val, 'to_messages'):
            messages = input_val.to_messages()
            for msg in messages:
                m_type = getattr(msg, 'type', '') or msg.__class__.__name__.lower()
                if 'system' in m_type:
                    system_text = str(msg.content)
                else:
                    user_text += f"\n{msg.content}"
        elif isinstance(input_val, dict):
            system_text = input_val.get('system_instruction', '')
            user_text = input_val.get('prompt', '') or input_val.get('user_context', '')
        else:
            user_text = str(input_val)

        user_text = user_text.strip()
        result = self.provider.generate(
            system_instruction=system_text,
            prompt=user_text,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return result.get('text') or ''


# ---------------------------------------------------------------------------
# 2. LangChain Document Converters
# ---------------------------------------------------------------------------

def product_to_langchain_doc(product: Any) -> Document:
    """Converts a Django Product model into a standardized LangChain Document."""
    specs = ''
    if isinstance(getattr(product, 'specifications', None), dict):
        specs = ' '.join(f'{k}: {v}' for k, v in product.specifications.items())

    content = (
        f"Title: {product.name}\n"
        f"Brand: {getattr(product, 'brand', '')}\n"
        f"Category: {getattr(product, 'category', '')}\n"
        f"Price: Rs. {product.price}\n"
        f"Description: {getattr(product, 'description', '') or ''}\n"
        f"Specs: {specs}"
    )

    metadata = {
        'id': str(product.id),
        'kind': 'product',
        'price': float(product.price),
        'rating': float(getattr(product, 'rating', 0) or 0),
        'stock': int(getattr(product, 'stock', 0) or 0),
        'seller': getattr(product, 'seller', '') or '',
    }
    return Document(page_content=content, metadata=metadata)


def policy_to_langchain_doc(topic: str, text: str) -> Document:
    """Converts a marketplace policy rule into a LangChain Document."""
    return Document(page_content=text, metadata={'kind': 'policy', 'topic': topic})


# ---------------------------------------------------------------------------
# 3. Pydantic Schemas for Structured Tool Calling & Outputs
# ---------------------------------------------------------------------------

class SearchCatalogArgs(BaseModel):
    query: str = Field(description="Search keywords, product name, or category")
    max_price: Optional[float] = Field(default=None, description="Optional upper price limit in INR")
    category: Optional[str] = Field(default=None, description="Optional category filter (e.g. Electronics, Fashion)")

class CheckOrderStatusArgs(BaseModel):
    order_id: str = Field(description="Order ID, e.g. ORD-2026-001 or ord-ai-1234")
    customer_email: Optional[str] = Field(default=None, description="Authenticated customer email for ownership verification")

class AddToCartArgs(BaseModel):
    product_id: str = Field(description="The unique product ID to add to cart")
    quantity: int = Field(default=1, description="Quantity of items to add, minimum 1")
    user_email: Optional[str] = Field(default=None, description="Optional customer email")

class AdminAuditArgs(BaseModel):
    user_role: str = Field(description="Role of requesting user; must be ADMIN or STAFF")
    application_id: Optional[str] = Field(default=None, description="Optional seller application ID to audit")


# ---------------------------------------------------------------------------
# 4. LangChain Tools (@tool)
# ---------------------------------------------------------------------------

@tool(args_schema=SearchCatalogArgs)
def search_catalog_tool(query: str, max_price: Optional[float] = None, category: Optional[str] = None) -> str:
    """Search AutoCart catalog for products matching a natural language query and optional constraints."""
    from .models import Product
    qs = Product.objects.all()
    if max_price:
        qs = qs.filter(price__lte=max_price)
    if category:
        qs = qs.filter(category__icontains=category)
    
    q_low = query.lower()
    results = [p for p in qs if q_low in p.name.lower() or q_low in (p.category or '').lower() or q_low in (getattr(p, 'brand', '') or '').lower()][:5]
    if not results:
        # Fallback to broader price/category filter if specific name didn't match
        results = list(qs[:5])
    if not results:
        return "No matching products found in AutoCart catalog."
    return "\n".join([f"- [{p.id}] {p.name} | Rs. {p.price:,.0f} | Rating: {getattr(p, 'rating', 0)} | Stock: {getattr(p, 'stock', 0)}" for p in results])


@tool
def get_product_details_tool(product_id: str) -> str:
    """Retrieve full details, price, inventory status, and specifications for a single product by ID."""
    from .models import Product
    prod = Product.objects.filter(id=product_id.strip()).first()
    if not prod:
        return f"Product '{product_id}' was not found in AutoCart database."
    specs = json.dumps(prod.specifications) if isinstance(prod.specifications, dict) else str(prod.specifications or '')
    return (
        f"Product: {prod.name} (ID: {prod.id})\n"
        f"Price: Rs. {prod.price:,.0f} | Discount: {getattr(prod, 'discount', 0)}%\n"
        f"Stock: {prod.stock} units available\n"
        f"Rating: {getattr(prod, 'rating', 0)} ({getattr(prod, 'reviewCount', 0)} reviews)\n"
        f"Brand: {getattr(prod, 'brand', '')} | Category: {getattr(prod, 'category', '')}\n"
        f"Description: {prod.description or 'No description'}\n"
        f"Specs: {specs}"
    )


@tool(args_schema=CheckOrderStatusArgs)
def check_order_status_tool(order_id: str, customer_email: Optional[str] = None) -> str:
    """Retrieve fulfillment and delivery status for an existing order with customer authorization."""
    from .models import Order
    clean_id = order_id.strip()
    order = Order.objects.filter(id__iexact=clean_id).first()
    if not order:
        return f"Order '{order_id}' was not found in AutoCart records."
    
    # Customer Privacy Guard: if customer_email is provided, verify ownership
    if customer_email and order.customerEmail:
        if order.customerEmail.strip().lower() != customer_email.strip().lower():
            return f"Unauthorized: Order '{order_id}' is registered to another customer account."

    return (
        f"Order {order.id}: Status '{order.status}' | Total Rs. {order.totalAmount:,.0f} | "
        f"Date: {order.date} | Payment: {getattr(order, 'paymentStatus', 'PAID')} | "
        f"Items: {len(order.items or [])}"
    )


@tool
def get_marketplace_policy_tool(topic: str) -> str:
    """Retrieve marketplace policy regarding delivery, returns, pickup, cancellation, or payments."""
    from .agent_graph import POLICY
    low = topic.lower()
    for key, text in POLICY:
        if key in low:
            return text
    return POLICY[0][1]


@tool(args_schema=AddToCartArgs)
def add_to_cart_tool(product_id: str, quantity: int = 1, user_email: Optional[str] = None) -> str:
    """Add a verified product to the customer shopping cart after checking stock availability."""
    from .models import Product
    from .agents import tools as tool_lib
    
    prod = Product.objects.filter(id=product_id.strip()).first()
    if not prod:
        return f"Error: Product '{product_id}' does not exist in catalog."
    if prod.stock < quantity:
        return f"Error: Only {prod.stock} items left in stock for '{prod.name}'. Cannot add {quantity}."
    
    res = tool_lib.add_to_cart_tool(product_id=prod.id, quantity=quantity, user_email=user_email)
    if res.get('success'):
        summary = res.get('cartSummary', {})
        subtotal = summary.get('subtotal', prod.price * quantity)
        return f"Success: Added {quantity}x '{prod.name}' to cart. Cart subtotal is now Rs. {subtotal:,.0f}."
    return f"Failed to add to cart: {res.get('error', 'Unknown error')}"


@tool(args_schema=AdminAuditArgs)
def admin_audit_applications_tool(user_role: str, application_id: Optional[str] = None) -> str:
    """Audit pending seller applications and inspect risk factors. Restricted to ADMIN and STAFF."""
    if user_role not in ('ADMIN', 'STAFF'):
        return "Access Denied: You must be an authenticated administrator or staff member."
    
    from .agents import tools as tool_lib
    if application_id:
        risk_res = tool_lib.explain_application_risk(application_id, user_role)
        if not risk_res.get('found'):
            return f"Application '{application_id}' not found."
        factors = ", ".join([f.get('factor', '') for f in risk_res.get('contributingFactors', [])]) or "None"
        return (
            f"Audit for {risk_res.get('companyName')} ({risk_res.get('applicationId')}): "
            f"Risk Score {risk_res.get('riskScore')}/100 ({risk_res.get('riskCategory')}). "
            f"Recommended Action: {risk_res.get('recommendedAction')}. "
            f"Risk factors: {factors}."
        )
    
    summary = tool_lib.summarize_pending_applications(user_role)
    apps = summary.get('applications', [])
    return f"Found {len(apps)} pending applications awaiting review. Total pending count: {summary.get('pendingCount', len(apps))}."


LANGCHAIN_TOOLS = [
    search_catalog_tool,
    get_product_details_tool,
    check_order_status_tool,
    get_marketplace_policy_tool,
    add_to_cart_tool,
    admin_audit_applications_tool,
]


# ---------------------------------------------------------------------------
# 5. LangChain Expression Language (LCEL) Chains
# ---------------------------------------------------------------------------

SAATHI_SYSTEM_PROMPT = (
    "You are Saathi, the friendly shopping assistant of AutoCart, a marketplace of local Mumbai stores. "
    "Use ONLY the FACTS provided. Never invent products, prices, stock, discounts or policies. "
    "Keep it under 60 words, warm and plain. Do not list every product (cards show them); say which one you would pick and why, using the ratings and price. "
    "If the facts do not answer the question, say so and offer to bring in a person."
)

MUNIM_SYSTEM_PROMPT = (
    "You are Munim, the AutoCart seller's shop-keeping assistant (munim means the traditional shop accountant). "
    "Answer the seller's question using ONLY the FACTS JSON. Use rupees (₹). Be specific: name products and numbers. "
    "Keep it under 70 words, warm and practical, and end with one concrete next step when useful. "
    "If the facts do not contain the answer, say so plainly. Never invent figures, customers or products."
)

DISCOVERY_SYSTEM_PROMPT = (
    "You are the AutoCart Discovery & Shopping Agent, an expert e-commerce shopping consultant. "
    "Use ONLY the verified catalog matches provided in the prompt. Never invent products, prices, or specs. "
    "Provide a friendly, concise 2-3 sentence overview highlighting top picks, price range, and encourage the customer to ask for details or add to cart. "
    "Keep the tone professional, helpful, and natural."
)

CUSTOMER_ENGAGEMENT_SYSTEM_PROMPT = (
    "You are the AutoCart Customer Engagement & Support Agent, an empathetic post-purchase and order specialist. "
    "Ground every statement in verified order status, tracking, and policies. "
    "Never disclose details of orders belonging to other customers. Keep responses clear, warm, and concise."
)

ADMIN_ASSISTANT_SYSTEM_PROMPT = (
    "You are the AutoCart Admin Assistance Agent. "
    "You assist marketplace administrators in auditing onboarding applications, reviewing compliance risk scores, and summarizing operations. "
    "Operate strictly within the admin perimeter. Do not execute destructive actions automatically; provide structured recommendations for human review."
)


def get_saathi_lcel_chain(temperature: float = 0.4, max_tokens: int = 300):
    """
    Constructs the LangChain LCEL pipeline for Saathi:
    ChatPromptTemplate -> LangChainLLMRunnable -> StrOutputParser
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", SAATHI_SYSTEM_PROMPT),
        ("human", "Customer first name: {customer_name}\n"
                  "What we know about them: {user_memory}\n"
                  "FACTS:\n{facts}\n"
                  "QUESTION: {question}"),
    ])
    llm = RunnableLambda(LangChainLLMRunnable(temperature=temperature, max_tokens=max_tokens))
    parser = StrOutputParser()
    return prompt | llm | parser


def get_munim_lcel_chain(temperature: float = 0.3, max_tokens: int = 400):
    """
    Constructs the LangChain LCEL pipeline for Munim:
    ChatPromptTemplate -> LangChainLLMRunnable -> StrOutputParser
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", MUNIM_SYSTEM_PROMPT),
        ("human", "Seller first name: {seller_name}\n"
                  "FACTS: {facts}\n"
                  "QUESTION: {question}"),
    ])
    llm = RunnableLambda(LangChainLLMRunnable(temperature=temperature, max_tokens=max_tokens))
    parser = StrOutputParser()
    return prompt | llm | parser


def get_discovery_lcel_chain(temperature: float = 0.2, max_tokens: int = 300):
    """
    Constructs the LangChain LCEL pipeline for Product Discovery:
    ChatPromptTemplate -> LangChainLLMRunnable -> StrOutputParser
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", DISCOVERY_SYSTEM_PROMPT),
        ("human", "Customer Query: {query}\n\n"
                  "Verified Catalog Matches:\n{catalog_matches}\n\n"
                  "Provide a friendly, concise 2-3 sentence overview highlighting top recommendations and prices."),
    ])
    llm = RunnableLambda(LangChainLLMRunnable(temperature=temperature, max_tokens=max_tokens))
    parser = StrOutputParser()
    return prompt | llm | parser


def get_customer_engagement_lcel_chain(temperature: float = 0.3, max_tokens: int = 350):
    """
    Constructs the LangChain LCEL pipeline for Customer Engagement:
    ChatPromptTemplate -> LangChainLLMRunnable -> StrOutputParser
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", CUSTOMER_ENGAGEMENT_SYSTEM_PROMPT),
        ("human", "Customer Query: {query}\n\n"
                  "Verified Order Details & Status:\n{order_facts}\n\n"
                  "Cart Summary:\n{cart_facts}\n\n"
                  "Draft an empathetic, accurate, and concise reply."),
    ])
    llm = RunnableLambda(LangChainLLMRunnable(temperature=temperature, max_tokens=max_tokens))
    parser = StrOutputParser()
    return prompt | llm | parser


def get_admin_audit_lcel_chain(temperature: float = 0.2, max_tokens: int = 450):
    """
    Constructs the LangChain LCEL pipeline for Admin Operations:
    ChatPromptTemplate -> LangChainLLMRunnable -> StrOutputParser
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", ADMIN_ASSISTANT_SYSTEM_PROMPT),
        ("human", "Admin Request: {query}\n\n"
                  "Audit Facts & Risk Scores:\n{audit_facts}\n\n"
                  "Provide a structured audit summary with recommended human actions."),
    ])
    llm = RunnableLambda(LangChainLLMRunnable(temperature=temperature, max_tokens=max_tokens))
    parser = StrOutputParser()
    return prompt | llm | parser
