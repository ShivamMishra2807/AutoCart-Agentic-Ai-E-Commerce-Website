"""
AutoCart Multi-Agent Orchestrator Engine.
Coordinates 6 specialized agents with bounded tool-calling architecture:
- Agent A: Discovery & Shopping Agent (Catalog, budget, nearby physical stores)
- Agent B: Customer Engagement & Support Agent (Orders, fulfillment tracking, returns)
- Agent C: Location & Fulfillment Agent (Nearby store inventory, quotes, stock reservation)
- Agent D: Seller Onboarding & Verification Agent (OCR validation, risk assessment)
- Agent E: Seller Business Assistant Agent (Listing generation, stock health, price benchmark)
- Agent F: Admin Marketplace Assistant Agent (Application audit, risk highlights, operations)
"""

import json
import logging
import re
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

from django.db.models import Q
from .llm_provider import UnifiedLLMProvider
from .memory import SessionMemoryManager, ORDINALS
from . import tools as tool_lib
from ..models import (
    AgentTask, AgentExecutionLog, Product, Order, Store, StoreInventory, User,
    Seller, SellerApplication, SellerApplicationAudit
)
from ..fulfillment_service import FulfillmentService
from ..location_service import resolve_coordinates, haversine_distance_km, find_nearby_stores_with_inventory, extract_location_from_text

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Specialized System Instructions for Each Agent
# ---------------------------------------------------------------------------

DISCOVERY_SYSTEM_INSTRUCTION = """
You are the AutoCart Discovery & Shopping Agent, a friendly and knowledgeable e-commerce shopping advisor.

HOW TO ANSWER:
1. Speak naturally like an expert shopping consultant in clean, conversational sentences.
2. DO NOT output repetitive raw markdown headings like "### Top Recommendation" or bullet dumps of technical fields.
3. Provide a concise 2-3 sentence overview highlighting the top picks, price, key benefits, and why they fit the user's needs. The interactive product cards are already displayed below your message.
4. If nearby stores or in-stock local physical stores are found, clearly mention which nearby partner has it in stock for immediate delivery or pickup.
5. Grounding: ONLY recommend items provided in the catalog matches. Never invent products or prices.
"""

CUSTOMER_ENGAGEMENT_SYSTEM_INSTRUCTION = """
You are the AutoCart Customer Engagement & Support Agent, an empathetic shopping and post-purchase specialist.
You assist customers with live order tracking, delivery timelines, return policies, cart totals, and cancellations.

CORE RULES:
1. Customer Privacy: Order records are strictly scoped to the authenticated customer. Never disclose details from any other user.
2. Grounding: Use verified order status and tracking tools. Never claim an order is delivered, shipped, or refunded without backend confirmation.
3. Policy Guidance: Inform users clearly about return windows (7-day window) and eligibility conditions.
4. Keep answers concise, empathetic, and action-oriented.
"""

LOCATION_FULFILLMENT_SYSTEM_INSTRUCTION = """
You are the AutoCart Location & Fulfillment Agent.
You connect customers with nearby physical partner stores holding live inventory, calculate road delivery estimates, and coordinate stock reservations.

CORE RULES:
1. Grounding: Only recommend stores that genuinely have verified available stock in the database.
2. Distance & Transparency: Transparently explain distance in kilometers, estimated delivery time in minutes, and delivery fee.
3. Explain Why: State why the recommended store was chosen (e.g. closest distance, fastest delivery, best price).
"""

SELLER_ONBOARDING_SYSTEM_INSTRUCTION = """
You are the AutoCart Seller Onboarding & Verification Agent for the marketplace administration portal.
Your job is to assist sellers in submitting valid applications, analyze document OCR credentials, and produce structured assessments for admins.

CORE RULES:
1. Strict Role Protection: Final approval or activation is strictly restricted to authorized human administrators. You must NEVER self-approve an application.
2. Impartial Verification: Highlight missing fields (GSTIN, PAN, bank proof) and identify document OCR discrepancies.
3. Structure: Provide clear verified facts, risk scores, and recommended administrator next steps.
"""

SELLER_ASSISTANT_SYSTEM_INSTRUCTION = """
You are the AutoCart Seller Business Assistant, an expert e-commerce growth copilot.
You assist sellers with creating optimized product listings, competitive price benchmarking from market catalog data, and low-inventory replenishment alerts.

CORE RULES:
1. Draft Only: Product listings are drafted automatically for review. Inform the seller that explicit confirmation is required before publishing live.
2. Factual Pricing: Use real marketplace pricing benchmarks. Never invent market trends.
"""

ADMIN_ASSISTANT_SYSTEM_INSTRUCTION = """
You are the AutoCart Admin Assistance Agent.
You help marketplace operations teams audit pending seller applications across the 8-state application lifecycle, highlight high-risk discrepancies, and summarize inventory metrics.

CORE RULES:
1. Admin Authorization: This agent operates strictly within the secure admin perimeter.
2. Human in the Loop: Highlight high-risk applications needing investigation. Do not execute destructive actions automatically.
"""


class AgentEngine:
    """
    Central AutoCart AI Orchestrator that coordinates specialized agents with bounded tools.
    """

    def __init__(self):
        self.provider = UnifiedLLMProvider()

    def _log_tool_execution(
        self,
        task: Optional[AgentTask],
        agent_name: str,
        tool_name: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        execution_time_ms: int,
        status: str = 'SUCCESS'
    ):
        """Records an execution trace in the database for auditing and explainability."""
        try:
            AgentExecutionLog.objects.create(
                id=f"log-{uuid.uuid4().hex[:8]}",
                task=task,
                agentName=agent_name,
                toolName=tool_name,
                inputs=inputs,
                outputs=outputs,
                executionTimeMs=execution_time_ms,
                status=status
            )
        except Exception as e:
            logger.debug("Failed to record agent execution log: %s", e)

    # -----------------------------------------------------------------------
    # AGENT A & SATHI: DISCOVERY, RECOMMENDATION & CONVERSATIONAL SHOPPING
    # -----------------------------------------------------------------------
    def run_sathi(
        self,
        query: str,
        session_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        cart_items: Optional[List[Dict[str, Any]]] = None,
        customer_lat: Optional[float] = None,
        customer_lng: Optional[float] = None,
        pincode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Master Sathi Shopping & Discovery Orchestrator.
        Guarantees structured conversation state, exact ordinal & superlative resolution,
        live database grounding, cart additions/updates, and bounded fallbacks.
        """
        t0 = time.time()
        session_key = SessionMemoryManager.get_session_key(session_id, customer_email)
        state = SessionMemoryManager.get_state(session_key)
        q_clean = (query or '').strip()
        q_lower = q_clean.lower()
        tools_executed = []

        # Check location availability and resolve Mumbai MMR coordinates
        has_known_location = False
        effective_pincode = (pincode or '').strip() or state.get('pincode_context')
        saved_addr = state.get('delivery_address') or {}
        resolved_area = ""

        # Check if the query itself specifies a location, zone, or PIN code (e.g., "stores nearby klayan", "stores near thane")
        query_loc = extract_location_from_text(q_lower)
        if query_loc:
            effective_lat, effective_lng, resolved_area, matched_loc = query_loc
            has_known_location = True
            if matched_loc.isdigit() and len(matched_loc) == 6:
                effective_pincode = matched_loc

        # Check authenticated user's saved addresses in database if location not yet resolved
        if not has_known_location and not effective_pincode and customer_email:
            try:
                user_obj = User.objects.filter(email__iexact=customer_email).first()
                if user_obj and user_obj.addresses:
                    for addr in user_obj.addresses:
                        p = str(addr.get('pinCode') or addr.get('pincode') or '').strip()
                        if p and len(p) == 6:
                            effective_pincode = p
                            saved_addr = addr
                            break
            except Exception:
                pass

        if not has_known_location:
            if effective_pincode:
                coords = resolve_coordinates(effective_pincode)
                if coords:
                    effective_lat, effective_lng, resolved_area = coords
                    has_known_location = True
                else:
                    effective_lat, effective_lng = 19.0760, 72.8777
            elif customer_lat is not None and customer_lng is not None and (
                abs(float(customer_lat) - 12.9716) > 0.01 or abs(float(customer_lng) - 77.5946) > 0.01
            ):
                effective_lat, effective_lng = float(customer_lat), float(customer_lng)
                has_known_location = True
            else:
                effective_lat, effective_lng = 19.0760, 72.8777
                has_known_location = False

        # Sync active cart items in state
        active_cart = list(cart_items if cart_items is not None else state.get('cart_items', []))
        SessionMemoryManager.update_state(session_key, {'cart_items': active_cart})

        # Rehydrate displayed products from DB chat messages if in-memory state is empty
        displayed = state.get('displayed_products') or []
        if not displayed and session_id:
            try:
                from ..models import ChatMessage
                last_msg = ChatMessage.objects.filter(session_id=session_id, role='assistant').exclude(cards=[]).order_by('-createdAt').first()
                if last_msg and last_msg.cards:
                    prod_cards = [c for c in last_msg.cards if c.get('type') == 'product']
                    if prod_cards:
                        SessionMemoryManager.set_recommendations(session_key, prod_cards)
                        state = SessionMemoryManager.get_state(session_key)
                        displayed = prod_cards
            except Exception:
                pass

        # -------------------------------------------------------------------
        # INTENT 0: GREETING & CASUAL HELLO
        # -------------------------------------------------------------------
        if re.fullmatch(r"\s*(hi|hello|hey|hii+|namaste|good (morning|afternoon|evening)|thanks?( you)?|thank you|ok(ay)?)\W*", q_lower):
            greeting_name = customer_email.split('@')[0].capitalize() if customer_email else ''
            lead = f"Hello {greeting_name}! " if greeting_name else "Hello! "
            reply_text = f"{lead}I am Sathi, your AutoCart shopping companion. Tell me what you're looking for (e.g. \"wireless earbuds under ₹2,000\" or \"laptops for coding\"), or ask about your orders!"
            SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', ['greeting'])
            return {
                'agent': 'sathi',
                'status': 'success',
                'reply': reply_text,
                'products': [],
                'cards': [],
                'suggestedActions': ['Suggest wireless earbuds under ₹2,000', 'Laptops under ₹60,000', 'Track my order'],
                'toolsExecuted': ['greeting']
            }

        # INTENT 0-NEG: NEGATIVE ACKNOWLEDGMENT OR DECLINE ("No", "Nah", "No thanks")
        if re.fullmatch(r"\s*(no|no thanks|nope|nah|nahi|not now|no need|nothing|don'?t want)\W*", q_lower):
            reply_text = "No problem! Let me know whenever you'd like to explore products, find local stores, or check your orders."
            SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', ['decline'])
            return {
                'agent': 'sathi',
                'status': 'success',
                'reply': reply_text,
                'products': [],
                'cards': [],
                'suggestedActions': ['Laptops under ₹60,000', 'Top electronics', 'Track my order'],
                'toolsExecuted': ['decline']
            }

        # -------------------------------------------------------------------
        # INTENT 0A: PIN CODE ENTRY & LOCATION RESOLUTION (AWAITING_PINCODE OR EXPLICIT PIN)
        # -------------------------------------------------------------------
        is_pending_pin = (state.get('pending_action') == 'AWAITING_PINCODE_FOR_STORES')
        is_pure_digits = bool(re.fullmatch(r'\s*\d{3,8}\s*', q_clean))
        has_pin_keyword = bool(re.search(r'\b(?:pin|pincode|pin code)\b', q_lower))
        has_my_pin = bool(re.search(r'\bmy pin\b', q_lower))
        loc_from_query = extract_location_from_text(q_clean)

        if is_pending_pin or (is_pure_digits and len(q_clean.strip()) in (5, 6, 7)) or ((has_pin_keyword or has_my_pin) and re.search(r'\b\d+\b', q_clean)) or (is_pending_pin and bool(loc_from_query)):
            digits_match = re.search(r'\b\d+\b', q_clean)
            candidate_pin = digits_match.group(0) if digits_match else ''
            target_prod = state.get('selected_product') or (displayed[0] if displayed else None)

            # Check if user entered an area/city name (e.g. "kalyan", "klayan", "thane") instead of a PIN code
            if loc_from_query and not candidate_pin:
                pin_lat, pin_lng, pin_area, matched_alias = loc_from_query
                resolved = (pin_lat, pin_lng, pin_area)
                candidate_pin = matched_alias if matched_alias.isdigit() else ''
            else:
                # 1. Format validation: Indian postal codes must be exactly 6 digits
                if not candidate_pin or len(candidate_pin) != 6 or not candidate_pin.isdigit():
                    reply_text = (
                        "Please enter a valid 6-digit PIN code (for example: 400053, 400601, 421301) "
                        "or area name (e.g. Kalyan, Thane, Andheri) so I can find nearby stores for you."
                    )
                    SessionMemoryManager.update_state(session_key, {
                        'pending_action': 'AWAITING_PINCODE_FOR_STORES',
                        'selected_product': target_prod,
                        'selected_product_id': target_prod['id'] if target_prod else None
                    })
                    SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', ['validate_pincode_format'])
                    return {
                        'agent': 'sathi',
                        'status': 'error',
                        'reply': reply_text,
                        'pendingAction': 'AWAITING_PINCODE_FOR_STORES',
                        'products': [target_prod] if target_prod else [],
                        'cards': [target_prod] if target_prod else [],
                        'nearbyStores': [],
                        'toolsExecuted': ['validate_pincode_format']
                    }

                # 2. Coverage resolution in Mumbai MMR database
                resolved = resolve_coordinates(candidate_pin)
            if not resolved:
                reply_text = (
                    f"We currently do not service PIN code {candidate_pin}. AutoCart currently provides "
                    f"hyperlocal store discovery and delivery across the Mumbai Metropolitan Region "
                    f"(including Mumbai, Thane, Kalyan, Dombivli, Mulund, Bhandup, Ghatkopar, Powai, Andheri, Borivali, and Navi Mumbai). "
                    f"Please enter a supported 6-digit Mumbai PIN code or select a saved address."
                )
                SessionMemoryManager.update_state(session_key, {
                    'pending_action': 'AWAITING_PINCODE_FOR_STORES',
                    'selected_product': target_prod,
                    'selected_product_id': target_prod['id'] if target_prod else None
                })
                SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', ['resolve_pincode_coverage'])
                return {
                    'agent': 'sathi',
                    'status': 'unsupported_area',
                    'reply': reply_text,
                    'pendingAction': 'AWAITING_PINCODE_FOR_STORES',
                    'products': [target_prod] if target_prod else [],
                    'cards': [target_prod] if target_prod else [],
                    'nearbyStores': [],
                    'toolsExecuted': ['resolve_pincode_coverage']
                }

            # 3. Successful PIN resolution
            pin_lat, pin_lng, pin_area = resolved
            effective_lat, effective_lng = pin_lat, pin_lng
            effective_pincode = candidate_pin
            resolved_area = pin_area
            has_known_location = True

            SessionMemoryManager.set_delivery_address(
                session_key,
                {'pinCode': candidate_pin, 'area': pin_area, 'lat': pin_lat, 'lng': pin_lng},
                pin_code=candidate_pin
            )
            SessionMemoryManager.update_state(session_key, {
                'pending_action': None,
                'pincode_context': candidate_pin
            })
            tools_executed.append('resolve_pincode')

            # Execute store search for resolved location and preserved target product
            nearby_stores = find_nearby_stores_with_inventory(
                product_id=target_prod['id'] if target_prod else None,
                customer_lat=effective_lat,
                customer_lng=effective_lng,
                max_radius_km=30.0,
                required_quantity=1,
                pin_code=effective_pincode
            )
            SessionMemoryManager.update_state(session_key, {
                'last_stores': nearby_stores,
                'selected_store': nearby_stores[0] if nearby_stores else None,
            })
            tools_executed.append('find_nearby_stores_for_product')

            loc_label = resolved_area or f"PIN {effective_pincode}"
            approx_notice = f"*(Note: PIN code {effective_pincode} represents an approximate area around {loc_label}, not an exact street address)*"

            if nearby_stores:
                best = nearby_stores[0]
                store_list_text = []
                for idx, s in enumerate(nearby_stores[:3], 1):
                    fee_str = "Free Delivery" if s['deliveryFee'] == 0 else f"₹{s['deliveryFee']:.0f} delivery fee"
                    avail_str = f"{s.get('availableQuantity', 0)} in stock" if s.get('availableQuantity') is not None else "In Stock"
                    store_list_text.append(
                        f"**{idx}. {s['storeName']}** (~{s['distanceKm']} km away)\n"
                        f"   📍 {s['address']}\n"
                        f"   ⏱️ Delivery in ~{s['estimatedMinutes']} mins • 🚚 {fee_str} • 📦 {avail_str}"
                    )
                stores_summary = "\n\n".join(store_list_text)

                if target_prod:
                    reply_text = (
                        f"📍 **Nearby Stores for {target_prod['name']}** near **{loc_label}**:\n\n"
                        f"{stores_summary}\n\n"
                        f"{approx_notice}\n\n"
                        f"Would you like to order from **{best['storeName']}** or add this item to your cart?"
                    )
                else:
                    reply_text = (
                        f"📍 **Nearby Stores in Mumbai MMR** near **{loc_label}**:\n\n"
                        f"{stores_summary}\n\n"
                        f"{approx_notice}"
                    )

                SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', tools_executed)
                return {
                    'agent': 'sathi',
                    'status': 'success',
                    'reply': reply_text,
                    'products': [target_prod] if target_prod else [],
                    'cards': [target_prod] if target_prod else [],
                    'nearbyStores': nearby_stores,
                    'toolsExecuted': tools_executed
                }
            else:
                tools_executed.append('suggest_alternatives')
                alts = []
                if target_prod:
                    target_cat = target_prod.get('category') or 'Electronics'
                    alts_qs = Product.objects.filter(category=target_cat, stock__gt=0).exclude(id=target_prod['id'])[:3]
                    if not alts_qs:
                        alts_qs = Product.objects.filter(stock__gt=0).exclude(id=target_prod['id'])[:3]
                    from ..serializers import ProductSerializer
                    alts = [ProductSerializer(p).data for p in alts_qs]

                if alts:
                    alt_lines = "\n".join([f"• **{a['name']}** - ₹{a['price']:,.0f} ({a.get('rating', 4.0)}★ • In Stock)" for a in alts])
                    reply_text = (
                        f"I checked nearby partner stores near **{loc_label}**, but **{target_prod['name']}** is currently out of stock "
                        f"at all nearby stores within our delivery coverage.\n\n"
                        f"Here are verified in-stock alternatives available for delivery:\n{alt_lines}\n\n"
                        f"{approx_notice}\n\n"
                        f"Would you like details on any of these alternatives?"
                    )
                else:
                    reply_text = (
                        f"No partner stores within 30 km of **{loc_label}** currently have verified in-store stock for this item. "
                        f"Standard warehouse shipping is available.\n\n{approx_notice}"
                    )

                SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', tools_executed)
                return {
                    'agent': 'sathi',
                    'status': 'out_of_stock_nearby',
                    'reply': reply_text,
                    'products': alts if alts else ([target_prod] if target_prod else []),
                    'cards': alts if alts else ([target_prod] if target_prod else []),
                    'nearbyStores': [],
                    'toolsExecuted': tools_executed
                }

        # -------------------------------------------------------------------
        # INTENT 0B: ORDER INQUIRIES, TRACKING, FULFILLMENT TIMELINE & CANCELLATIONS
        # -------------------------------------------------------------------
        is_order_inquiry = (
            any(phrase in q_lower for phrase in [
                'timeline', 'fulfillment timeline', 'delivery timeline', 'track order',
                'track my order', 'where is my order', 'order status', 'my order',
                'cancel order', 'cancel this order', 'order cancel', 'cancellation'
            ]) or (
                'cancel' in q_lower and ('order' in q_lower or bool(re.search(r'\b(?:ord-ai-[a-f0-9]+|ord-\d{4}-\d{3,6})\b', q_lower)))
            )
        ) and not any(phrase in q_lower for phrase in ['suggest', 'search', 'dikhao', 'earbuds', 'laptop', 'under', 'below', 'bag', 'cart'])

        if is_order_inquiry:
            return self.run_customer_engagement_agent(
                query=query,
                cart_items=active_cart,
                session_id=session_id,
                customer_email=customer_email
            )

        # -------------------------------------------------------------------
        # INTENT 1: CHEAPEST / SUPERLATIVE COMPARISON AMONG RECOMMENDED PRODUCTS
        # -------------------------------------------------------------------
        is_cheapest = any(w in q_lower for w in [
            'which one is the cheapest', 'which is the cheapest', 'which one is cheapest',
            'cheapest', 'sabse sasta', 'sasta kaunsa', 'lowest price', 'kam price',
            'sasta wala', 'least expensive', 'cheaper one'
        ]) and not any(w in q_lower for w in ['suggest', 'search', 'dikhao', 'show me', 'alternative'])

        if is_cheapest and displayed:
            tools_executed.append('compare_products')
            cheap_p = min(displayed, key=lambda p: float(p.get('price', 0)))
            cheap_idx = displayed.index(cheap_p) + 1
            other_prices = [float(p.get('price', 0)) for p in displayed if str(p.get('id')) != str(cheap_p.get('id'))]
            other_min = min(other_prices) if other_prices else float(cheap_p.get('price', 0))
            other_max = max(other_prices) if other_prices else float(cheap_p.get('price', 0))

            SessionMemoryManager.set_selected_product(session_key, cheap_p, quantity=1, pending_action='COMPARE')

            reply_text = (
                f"Among the {len(displayed)} recommended products, the cheapest is **{cheap_p['name']}** "
                f"(Option #{cheap_idx}) at **₹{cheap_p['price']:,.0f}** (rated {cheap_p.get('rating', 0)}★).\n\n"
                f"The other options range from ₹{other_min:,.0f} to ₹{other_max:,.0f}.\n\n"
                f"Would you like to add the #{cheap_idx} one to your cart?"
            )
            SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', tools_executed)
            return {
                'agent': 'sathi',
                'status': 'success',
                'reply': reply_text,
                'products': displayed,
                'cards': displayed,
                'selectedProductId': cheap_p['id'],
                'toolsExecuted': tools_executed,
                'suggestedActions': [f"Add the {ORDINALS.get(cheap_idx - 1, 'cheapest')} one to cart", "Compare first and third", "View cart"]
            }

        # -------------------------------------------------------------------
        # INTENT 2: CHEAPER ALTERNATIVE LOOKUP
        # -------------------------------------------------------------------
        if 'cheaper alternative' in q_lower or 'sasta alternative' in q_lower:
            base_p = state.get('selected_product') or (displayed[0] if displayed else None)
            if base_p:
                tools_executed.append('search_products')
                alts_res = tool_lib.search_products(
                    query=base_p.get('category', ''),
                    category=base_p.get('category'),
                    max_price=float(base_p['price']) - 1.0,
                    limit=4
                )
                alts = alts_res.get('products', [])
                if alts:
                    SessionMemoryManager.set_recommendations(session_key, alts)
                    reply_text = f"Here are cheaper alternatives to **{base_p['name']}** (which was ₹{base_p['price']:,.0f}):"
                    return {
                        'agent': 'sathi',
                        'status': 'success',
                        'reply': reply_text,
                        'products': alts,
                        'cards': alts,
                        'toolsExecuted': tools_executed
                    }

        # -------------------------------------------------------------------
        # INTENT 3: SIDE-BY-SIDE COMPARISON (e.g. "Compare the first and second products")
        # -------------------------------------------------------------------
        is_compare_specific = (
            'compare' in q_lower or 'dono compare' in q_lower or 'comparison' in q_lower or 'muqabla' in q_lower
        ) and not any(w in q_lower for w in ['suggest', 'search', 'dikhao', 'show me']) and bool(displayed)
        if is_compare_specific and displayed:
            cmp_prods, err = SessionMemoryManager.resolve_comparison_products(session_key, q_lower)
            if cmp_prods and len(cmp_prods) >= 2:
                tools_executed.append('compare_products')
                p1, p2 = cmp_prods[0], cmp_prods[1]
                price_diff = abs(float(p1['price']) - float(p2['price']))
                cheaper_name = p1['name'] if float(p1['price']) < float(p2['price']) else p2['name']
                reply_text = (
                    f"📊 **Comparison**: **{p1['name']}** vs **{p2['name']}**\n\n"
                    f"• **1. {p1['name']}**: ₹{p1['price']:,.0f} | ★{p1.get('rating', 0)} | {'In Stock' if p1.get('stock', 0) > 0 else 'Out of Stock'}\n"
                    f"• **2. {p2['name']}**: ₹{p2['price']:,.0f} | ★{p2.get('rating', 0)} | {'In Stock' if p2.get('stock', 0) > 0 else 'Out of Stock'}\n\n"
                    f"💡 **Verdict**: **{cheaper_name}** is more affordable by ₹{price_diff:,.0f}."
                )
                SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', tools_executed)
                return {
                    'agent': 'sathi',
                    'status': 'success',
                    'reply': reply_text,
                    'products': cmp_prods,
                    'cards': cmp_prods,
                    'toolsExecuted': tools_executed,
                    'suggestedActions': ['Add first one to cart', 'Add second one to cart', 'View cart']
                }

        # -------------------------------------------------------------------
        # INTENT 4: QUANTITY UPDATE ("Add two pieces", "Isko do quantity mein add kar")
        # -------------------------------------------------------------------
        is_qty_update = any(phrase in q_lower for phrase in [
            'add two pieces', 'add 2 pieces', 'pieces', 'piece', 'quantity', 'units',
            'do piece', 'teen piece', 'make it', 'update quantity', 'quantity mein add',
            'do quantity', 'teen quantity', 'chaar quantity', 'paanch quantity'
        ]) and not any(phrase in q_lower for phrase in ['suggest', 'search', 'dikhao', 'show me', 'wireless', 'earbuds', 'laptop', 'shoes'])

        if is_qty_update:
            target_qty = SessionMemoryManager.extract_quantity(q_lower) or 2
            resolved_p, res_type, err_msg = SessionMemoryManager.resolve_product_reference(session_key, q_lower)
            target_p = resolved_p or state.get('selected_product') or (displayed[0] if displayed else None)

            if not target_p:
                reply_text = "Which product would you like to update the quantity for? Please search for a product first."
                return {'agent': 'sathi', 'status': 'clarification', 'reply': reply_text, 'products': []}

            tools_executed.append('update_cart_quantity')
            cart_res = tool_lib.update_cart_quantity_tool(
                product_id=target_p['id'],
                quantity=target_qty,
                cart_items=active_cart,
                user_email=customer_email
            )
            SessionMemoryManager.update_state(session_key, {
                'quantity': target_qty,
                'selected_product': target_p,
                'selected_product_id': target_p['id'],
                'cart_items': cart_res.get('cartItems', active_cart)
            })

            reply_text = (
                f"✅ **Quantity Updated!**\n\n"
                f"I've updated the quantity for **{target_p['name']}** to **{target_qty} piece{'s' if target_qty > 1 else ''}** in your cart.\n"
                f"• **Unit Price**: ₹{float(target_p['price']):,.0f}\n"
                f"• **Item Subtotal**: ₹{float(target_p['price']) * target_qty:,.0f}\n"
                f"• **Updated Cart Total**: ₹{cart_res['cartSummary']['subtotal']:,.0f}\n\n"
                f"Ready to proceed to checkout or look for more items?"
            )
            SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', tools_executed)
            return {
                'agent': 'sathi',
                'status': 'success',
                'reply': reply_text,
                'cartAction': {
                    'type': 'UPDATE_QUANTITY',
                    'productId': target_p['id'],
                    'product': target_p,
                    'quantity': target_qty
                },
                'products': [target_p],
                'cards': [target_p],
                'selectedProductId': target_p['id'],
                'quantity': target_qty,
                'toolsExecuted': tools_executed,
                'suggestedActions': ['View cart summary', 'Proceed to checkout', 'Continue shopping']
            }

        # -------------------------------------------------------------------
        # INTENT 5: BUY / BUY INSTEAD ("Actually, buy the third one instead", "Dusra wala le lunga")
        # -------------------------------------------------------------------
        is_buy_intent = any(phrase in q_lower for phrase in [
            'buy the third one instead', 'buy third instead', 'buy instead',
            'actually buy', 'buy the third one', 'buy the second one', 'buy the first one',
            'dusra wala le lunga', 'doosra wala le lunga', 'pehla wala le lunga', 'teesra wala le lunga',
            'buy now', 'buy this one', 'buy the', 'order the', 'khareed lunga'
        ]) and not any(phrase in q_lower for phrase in ['suggest', 'search', 'dikhao', 'show me'])

        if is_buy_intent:
            resolved_p, res_type, err_msg = SessionMemoryManager.resolve_product_reference(session_key, q_lower)
            if err_msg:
                return {'agent': 'sathi', 'status': 'clarification', 'reply': err_msg, 'products': displayed}

            target_p = resolved_p or state.get('selected_product') or (displayed[0] if displayed else None)
            if not target_p:
                found = tool_lib.search_products(query, limit=1).get('products', [])
                target_p = found[0] if found else None

            if not target_p:
                reply_text = "Which product would you like to buy? Please search for a product first."
                return {'agent': 'sathi', 'status': 'clarification', 'reply': reply_text, 'products': []}

            tools_executed.append('check_product_availability')
            avail = tool_lib.check_product_availability(target_p['id'])
            if not avail.get('isAvailable'):
                alts = avail.get('alternatives', [])
                reply_text = f"**{target_p['name']}** is currently out of stock. Here are available in-stock options:"
                return {
                    'agent': 'sathi',
                    'status': 'out_of_stock',
                    'reply': reply_text,
                    'products': alts,
                    'cards': alts,
                    'toolsExecuted': tools_executed
                }

            is_switch = any(w in q_lower for w in ['instead', 'actually', 'nahi', 'change to', 'badle'])
            SessionMemoryManager.set_selected_product(session_key, target_p, quantity=1, pending_action='BUY_NOW')

            lead = f"👍 Switched your selection to **{target_p['name']}**!" if is_switch else f"Great pick! I've selected **{target_p['name']}**."
            reply_text = (
                f"{lead}\n\n"
                f"• **Price**: ₹{target_p['price']:,.0f}\n"
                f"• **Availability**: Verified In Stock ({target_p.get('stock', 10)} units left)\n\n"
                f"Check your order details below to confirm your purchase."
            )
            SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', tools_executed)
            return {
                'agent': 'sathi',
                'status': 'success',
                'reply': reply_text,
                'buyProductId': target_p['id'],
                'cartAction': {
                    'type': 'BUY_NOW',
                    'product': target_p,
                    'quantity': 1
                },
                'products': [target_p],
                'cards': [target_p],
                'selectedProductId': target_p['id'],
                'toolsExecuted': tools_executed,
                'suggestedActions': ['Confirm order', 'Check delivery address', 'Add accessories']
            }

        # -------------------------------------------------------------------
        # INTENT 6: ADD TO CART ("Add the second one to my cart", "Pehla wala cart mein daal")
        # -------------------------------------------------------------------
        is_add_cart = (
            any(phrase in q_lower for phrase in [
                'add the second one to my cart', 'add the second one', 'add second one',
                'add to cart', 'cart mein add', 'cart me add', 'cart me daal', 'cart mein daal',
                'add in cart', 'pehla wala cart', 'doosra wala cart', 'dusra wala cart', 'teesra wala cart',
                'put in cart', 'add kar de', 'add kar do', 'cart me daalo', 'cart mein daalo',
                'add first', 'add second', 'add third', 'add fourth', 'add fifth', 'add sixth',
                'add seventh', 'add eighth', 'add ninth', 'add tenth', 'add last'
            ]) or (
                ('add' in q_lower or 'daal' in q_lower or 'daalo' in q_lower) and ('cart' in q_lower or 'bag' in q_lower)
            ) or (
                'add' in q_lower and (
                    any(ord_word in q_lower for ord_word in [
                        'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth',
                        'last', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th',
                        'cheapest', 'this one', 'it', 'one'
                    ]) or bool(re.search(r'\b\d+(?:st|nd|rd|th)?\b', q_lower))
                )
            )
        )

        if is_add_cart:
            resolved_p, res_type, err_msg = SessionMemoryManager.resolve_product_reference(session_key, q_lower)
            if err_msg:
                return {'agent': 'sathi', 'status': 'clarification', 'reply': err_msg, 'products': displayed}

            target_p = resolved_p or state.get('selected_product') or (displayed[0] if displayed else None)
            if not target_p:
                reply_text = "Please search for a product first so I know which item you'd like to add to your cart."
                return {'agent': 'sathi', 'status': 'clarification', 'reply': reply_text, 'products': []}

            req_qty = SessionMemoryManager.extract_quantity(q_lower) or 1
            tools_executed.append('add_to_cart')
            cart_res = tool_lib.add_to_cart_tool(
                product_id=target_p['id'],
                quantity=req_qty,
                cart_items=active_cart,
                user_email=customer_email
            )

            if not cart_res.get('success'):
                alts = cart_res.get('alternatives', [])
                return {
                    'agent': 'sathi',
                    'status': 'error',
                    'reply': cart_res.get('error', 'Could not add to cart.'),
                    'products': alts,
                    'cards': alts,
                    'toolsExecuted': tools_executed
                }

            SessionMemoryManager.set_selected_product(session_key, target_p, quantity=req_qty, pending_action='ADD_TO_CART')
            SessionMemoryManager.update_state(session_key, {'cart_items': cart_res.get('cartItems', active_cart)})

            reply_text = (
                f"✅ **Added to Cart!**\n\n"
                f"I've added **{target_p['name']}** (Qty: {req_qty}, ₹{target_p['price']:,.0f}) to your cart.\n\n"
                f"• **Unit Price**: ₹{target_p['price']:,.0f}\n"
                f"• **Cart Subtotal**: ₹{cart_res['cartSummary']['subtotal']:,.0f} "
                f"({('Free Delivery Eligible!' if cart_res['cartSummary']['freeShippingEligible'] else 'Add ₹' + str(round(max(0, 500 - cart_res['cartSummary']['subtotal']), 0)) + ' more for Free Delivery')})\n\n"
                f"You can say *'Check nearby store availability'* to check local store stock across Mumbai, or *'View cart'*."
            )
            SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', tools_executed)
            return {
                'agent': 'sathi',
                'status': 'success',
                'reply': reply_text,
                'cartAction': {
                    'type': 'ADD_TO_CART',
                    'productId': target_p['id'],
                    'product': target_p,
                    'quantity': req_qty
                },
                'products': [target_p],
                'cards': [target_p],
                'selectedProductId': target_p['id'],
                'toolsExecuted': tools_executed,
                'suggestedActions': ['Check nearby store availability', 'View cart summary', 'Continue shopping']
            }

        # -------------------------------------------------------------------
        # INTENT 6.5: AFFIRMATION / CONFIRMATION ("Yes", "Haan", "Sure", "Proceed")
        # -------------------------------------------------------------------
        clean_words = [w for w in re.split(r'\W+', q_lower) if w]
        is_affirmation = len(clean_words) <= 3 and any(
            w in ['yes', 'yeah', 'yep', 'haan', 'ha', 'sure', 'ok', 'okay', 'proceed', 'confirm', 'theek', 'kardo']
            for w in clean_words
        ) and not any(w in q_lower for w in ['not', 'nahi', 'cancel', 'no'])

        if is_affirmation:
            pending_action = state.get('pending_action')
            sel_prod = state.get('selected_product') or (displayed[0] if displayed else None)

            if pending_action in ['COMPARE', 'RECOMMEND', 'ADD_TO_CART'] or (sel_prod and not state.get('selected_store')):
                tools_executed.append('add_to_cart')
                cart_res = tool_lib.add_to_cart_tool(
                    product_id=sel_prod['id'],
                    quantity=1,
                    cart_items=active_cart,
                    user_email=customer_email
                )
                SessionMemoryManager.update_state(session_key, {
                    'pending_action': None,
                    'cart_items': cart_res.get('cartItems', active_cart)
                })
                reply_text = (
                    f"✅ **Added to Cart!**\n\n"
                    f"I've added **{sel_prod['name']}** (Qty: 1, ₹{sel_prod['price']:,.0f}) to your cart.\n\n"
                    f"• **Unit Price**: ₹{sel_prod['price']:,.0f}\n"
                    f"• **Cart Subtotal**: ₹{cart_res['cartSummary']['subtotal']:,.0f}\n\n"
                    f"You can say *'Check nearby store availability'* to see local stores, or *'View cart summary'*."
                )
                SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', tools_executed)
                return {
                    'agent': 'sathi',
                    'status': 'success',
                    'reply': reply_text,
                    'cartAction': {
                        'type': 'ADD_TO_CART',
                        'productId': sel_prod['id'],
                        'product': sel_prod,
                        'quantity': 1
                    },
                    'products': [sel_prod],
                    'cards': [sel_prod],
                    'selectedProductId': sel_prod['id'],
                    'toolsExecuted': tools_executed,
                    'suggestedActions': ['Check nearby store availability', 'View cart summary', 'Continue shopping']
                }

        # -------------------------------------------------------------------
        # INTENT 6.8: STORE SELECTION ("Powai store", "AutoCart Powai Store", "Select first store")
        # -------------------------------------------------------------------
        is_store_select = (
            any(name_kw in q_lower for name_kw in ['powai', 'andheri', 'bandra', 'thane', 'kalyan', 'dombivli', 'mulund', 'ghatkopar', 'borivali', 'vashi', 'parel'])
            and any(w in q_lower for w in ['store', 'shop', 'outlet'])
            and not any(w in q_lower for w in ['order', 'buy', 'mangwao', 'khareed'])
        ) or any(phrase in q_lower for phrase in [
            'store select', 'select store', 'pick store', 'choose store', 'wala store', 'select first store', 'select second store'
        ])

        if is_store_select:
            matched_store = None
            for s in (state.get('last_stores') or []):
                s_name = s.get('storeName', '').lower()
                s_area = s.get('address', '').lower()
                if any(w in s_name or w in s_area for w in ['powai', 'andheri', 'bandra', 'thane', 'kalyan', 'dombivli', 'mulund', 'ghatkopar', 'borivali', 'vashi', 'parel'] if w in q_lower):
                    matched_store = s
                    break

            if not matched_store and state.get('last_stores'):
                if any(w in q_lower for w in ['first', 'pehle', '1st']):
                    matched_store = state['last_stores'][0]
                elif any(w in q_lower for w in ['second', 'doosre', 'dusre', '2nd']) and len(state['last_stores']) > 1:
                    matched_store = state['last_stores'][1]
                else:
                    matched_store = state['last_stores'][0]

            if matched_store:
                SessionMemoryManager.update_state(session_key, {
                    'selected_store': matched_store,
                    'pending_action': 'STORE_ORDER'
                })
                reply_text = (
                    f"🏪 Selected **{matched_store['storeName']}** (~{matched_store.get('distanceKm', 0)} km away)!\n"
                    f"• **Location**: {matched_store.get('address', 'Mumbai')}\n"
                    f"• **Estimated Delivery**: ~{matched_store.get('estimatedMinutes', 30)} mins\n\n"
                    f"Say *'Order from this store'* to place your order with immediate store fulfillment."
                )
                SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', ['select_store'])
                return {
                    'agent': 'sathi',
                    'status': 'success',
                    'reply': reply_text,
                    'nearbyStores': [matched_store],
                    'suggestedActions': ['Order from this store', 'View other stores', 'Continue shopping']
                }

        # -------------------------------------------------------------------
        # INTENT 7: DIRECT STORE ORDER & FULFILLMENT
        # -------------------------------------------------------------------
        is_store_order = any(phrase in q_lower for phrase in [
            'pehle store se order', 'pehli store se order', 'order from first store',
            'order from store', 'store se order', 'order from this store',
            'pehle store se mangwao', 'pehle store se khareed', 'place order from store',
            'store se order karna hai', 'order from 1st store', 'order pehle store',
            'order from powai store', 'order from andheri store', 'order from second store',
            'order from 2nd store', 'order this from store', 'order from that store',
            'buy from this store', 'buy from store', 'place order', 'confirm order'
        ]) or (is_affirmation and state.get('selected_store'))

        if is_store_order:
            target_prod = state.get('selected_product') or (displayed[0] if displayed else None)
            target_store = None

            # Resolve store from query if specific store mentioned
            for s in (state.get('last_stores') or []):
                s_name = s.get('storeName', '').lower()
                s_area = s.get('address', '').lower()
                if any(w in s_name or w in s_area for w in ['powai', 'andheri', 'bandra', 'thane', 'kalyan', 'dombivli', 'mulund', 'ghatkopar', 'borivali', 'vashi', 'parel'] if w in q_lower):
                    target_store = s
                    break

            if not target_store:
                target_store = state.get('selected_store') or ((state.get('last_stores') or [None])[0])

            if not target_store and target_prod:
                s_res = tool_lib.find_nearby_stores_for_product(
                    product_id=target_prod['id'],
                    lat=effective_lat,
                    lng=effective_lng,
                    radius_km=30.0
                )
                stores_found = s_res.get('stores', [])
                target_store = stores_found[0] if stores_found else None

            if not target_prod or not target_store:
                return {
                    'agent': 'sathi',
                    'status': 'error',
                    'reply': "Please search for a product and select a nearby store first to place a store order.",
                    'products': [],
                    'nearbyStores': []
                }

            quote = FulfillmentService.generate_checkout_quote(
                product_id=target_prod['id'],
                quantity=1,
                store_id=target_store['storeId'],
                customer_lat=effective_lat,
                customer_lng=effective_lng
            )
            res_result = FulfillmentService.create_stock_reservation(
                store_id=target_store['storeId'],
                product_id=target_prod['id'],
                quantity=1,
                user_email=customer_email or 'shopper@autocart.in'
            )
            order_id = f"ord-ai-{uuid.uuid4().hex[:6]}"
            order = Order.objects.create(
                id=order_id,
                customerName='Valued Customer',
                customerEmail=customer_email or 'shopper@autocart.in',
                customerPhone='+91 98200 12345',
                date=datetime.now().strftime('%Y-%m-%d'),
                totalAmount=quote['totalAmount'],
                subtotal=quote['subtotal'],
                tax=quote['tax'],
                shippingFee=quote['deliveryFee'],
                paymentMethod='Cash on Delivery',
                paymentStatus='Pending',
                status='Placed',
                shippingAddress={
                    'storeId': target_store['storeId'],
                    'storeName': target_store['storeName'],
                    'storeAddress': target_store['address'],
                    'deliveryAddress': 'Customer Delivery Address, Mumbai',
                    'city': target_store.get('city', 'Mumbai'),
                    'pincode': target_store.get('pincode', '400053')
                },
                items=[{
                    'id': target_prod['id'],
                    'name': target_prod['name'],
                    'price': target_prod['price'],
                    'quantity': 1,
                    'image': (target_prod.get('images') or [''])[0]
                }]
            )
            store_model = Store.objects.filter(id=target_store['storeId']).first()
            fulfillment = FulfillmentService.initiate_fulfillment(order, store=store_model)
            if res_result.get('success'):
                FulfillmentService.confirm_stock_reservation(res_result['reservationToken'])

            tools_executed = ['generate_checkout_quote', 'create_stock_reservation', 'create_order', 'initiate_fulfillment']
            reply_text = (
                f"🎉 **Order Placed & Allocated to Store!**\n\n"
                f"• **Order ID**: `#{order.id}`\n"
                f"• **Status**: Placed (Payment: Pending COD)\n"
                f"• **Fulfilling Store**: **{target_store['storeName']}**\n"
                f"• **Product**: **{target_prod['name']}** (Qty: 1)\n"
                f"• **Total Amount**: ₹{quote['totalAmount']:,.2f}\n"
                f"• **Estimated Delivery**: **~{quote['estimatedMinutes']} mins**\n"
                f"• **Tracking ID**: `{fulfillment.trackingNumber}`"
            )
            SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', tools_executed)
            return {
                'agent': 'sathi',
                'status': 'success',
                'reply': reply_text,
                'orderAction': {
                    'type': 'ORDER_CONFIRMED',
                    'orderId': order.id,
                    'store': target_store,
                    'quote': quote,
                    'trackingNumber': fulfillment.trackingNumber
                },
                'orders': [{
                    'id': order.id,
                    'status': 'Placed',
                    'date': order.date,
                    'totalAmount': order.totalAmount,
                    'paymentStatus': 'Pending',
                    'items': order.items
                }],
                'products': [target_prod],
                'nearbyStores': [target_store],
                'toolsExecuted': tools_executed
            }

        # -------------------------------------------------------------------
        # INTENT 8: HYPERLOCAL STORE AVAILABILITY CHECK
        # -------------------------------------------------------------------
        is_store_check = any(phrase in q_lower for phrase in [
            'show me nearby stores', 'find stores near me', 'which nearby store',
            'where can i buy this product nearby', 'mere aas paas kaunse stores hain',
            'is product ko nearby kahan se kharid sakta hoon', 'show me nearby stores that have this product',
            'nearby store', 'nearby stores', 'stores near me', 'stores near',
            'store near me', 'stores nearby', 'mere aas paas', 'aas paas kaunse',
            'aas-paas', 'aas paas ke store', 'kahan se kharid sakta hoon',
            'kaha se khareedu', 'nearby kahan', 'nearby shop', 'local store',
            'local stores', 'check nearby store availability', 'store availability',
            'available store', 'store me available', 'store mein available',
            'konsi store', 'kaha available', 'kahan available', 'kis store',
            'check store', 'check inventory'
        ])
        if is_store_check:
            # Resolve target product from reference or previous state
            target_prod = None
            prod_ref, _, _ = SessionMemoryManager.resolve_product_reference(session_key, query)
            if prod_ref:
                target_prod = prod_ref
            else:
                target_prod = state.get('selected_product') or (displayed[0] if displayed else None)

            # Check if query specifies a location name or PIN (e.g., "stores nearby klayan", "stores in Thane")
            if not has_known_location:
                loc_found = extract_location_from_text(q_lower)
                if loc_found:
                    effective_lat, effective_lng, resolved_area, matched_name = loc_found
                    has_known_location = True
                    if matched_name.isdigit() and len(matched_name) == 6:
                        effective_pincode = matched_name

            if target_prod:
                SessionMemoryManager.set_selected_product(
                    session_key,
                    target_prod,
                    pending_action='AWAITING_PINCODE_FOR_STORES' if not has_known_location else None
                )

            # If location is NOT known, prompt for 6-digit delivery PIN code
            if not has_known_location:
                tools_executed.append('request_delivery_pincode')
                SessionMemoryManager.update_state(session_key, {
                    'pending_action': 'AWAITING_PINCODE_FOR_STORES',
                    'selected_product': target_prod,
                    'selected_product_id': target_prod['id'] if target_prod else None
                })
                reply_text = "Please enter your 6-digit delivery PIN code so I can find nearby stores."
                SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', tools_executed)
                return {
                    'agent': 'sathi',
                    'status': 'awaiting_pincode',
                    'reply': reply_text,
                    'pendingAction': 'AWAITING_PINCODE_FOR_STORES',
                    'products': [target_prod] if target_prod else [],
                    'cards': [target_prod] if target_prod else [],
                    'nearbyStores': [],
                    'toolsExecuted': tools_executed
                }

            # If location IS known, query stores with inventory
            tools_executed.append('find_nearby_stores_for_product')
            prod_id_to_check = target_prod['id'] if target_prod else None
            nearby_stores = find_nearby_stores_with_inventory(
                product_id=prod_id_to_check,
                customer_lat=effective_lat,
                customer_lng=effective_lng,
                max_radius_km=30.0,
                required_quantity=1,
                pin_code=effective_pincode
            )

            SessionMemoryManager.update_state(session_key, {
                'last_stores': nearby_stores,
                'selected_store': nearby_stores[0] if nearby_stores else None,
                'pending_action': None
            })

            loc_label = resolved_area or (f"PIN {effective_pincode}" if effective_pincode else "your location")
            approx_notice = f"*(Note: PIN code {effective_pincode} represents an approximate area around {loc_label}, not an exact street address)*" if effective_pincode else ""

            if nearby_stores:
                best = nearby_stores[0]
                store_list_text = []
                for idx, s in enumerate(nearby_stores[:3], 1):
                    fee_str = "Free Delivery" if s['deliveryFee'] == 0 else f"₹{s['deliveryFee']:.0f} delivery fee"
                    avail_str = f"{s.get('availableQuantity', 0)} in stock" if s.get('availableQuantity') is not None else "In Stock"
                    store_list_text.append(
                        f"**{idx}. {s['storeName']}** (~{s['distanceKm']} km away)\n"
                        f"   📍 {s['address']}\n"
                        f"   ⏱️ Delivery in ~{s['estimatedMinutes']} mins • 🚚 {fee_str} • 📦 {avail_str}"
                    )
                stores_summary = "\n\n".join(store_list_text)

                if target_prod:
                    reply_text = (
                        f"📍 **Nearby Stores for {target_prod['name']}** near **{loc_label}**:\n\n"
                        f"{stores_summary}\n\n"
                        f"{approx_notice}\n\n"
                        f"Would you like to order from **{best['storeName']}** or add this item to your cart?"
                    )
                else:
                    reply_text = (
                        f"📍 **Nearby Stores in Mumbai MMR** near **{loc_label}**:\n\n"
                        f"{stores_summary}\n\n"
                        f"{approx_notice}"
                    )

                SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', tools_executed)
                return {
                    'agent': 'sathi',
                    'status': 'success',
                    'reply': reply_text,
                    'products': [target_prod] if target_prod else [],
                    'cards': [target_prod] if target_prod else [],
                    'nearbyStores': nearby_stores,
                    'toolsExecuted': tools_executed
                }
            else:
                tools_executed.append('suggest_alternatives')
                alts = []
                if target_prod:
                    target_cat = target_prod.get('category') or 'Electronics'
                    alts_qs = Product.objects.filter(category=target_cat, stock__gt=0).exclude(id=target_prod['id'])[:3]
                    if not alts_qs:
                        alts_qs = Product.objects.filter(stock__gt=0).exclude(id=target_prod['id'])[:3]
                    from ..serializers import ProductSerializer
                    alts = [ProductSerializer(p).data for p in alts_qs]

                if alts:
                    alt_lines = "\n".join([f"• **{a['name']}** - ₹{a['price']:,.0f} ({a.get('rating', 4.0)}★ • In Stock)" for a in alts])
                    reply_text = (
                        f"I checked nearby partner stores near **{loc_label}**, but **{target_prod['name']}** is currently out of stock "
                        f"at all partner stores within our delivery coverage.\n\n"
                        f"Here are verified in-stock alternatives available for delivery:\n{alt_lines}\n\n"
                        f"{approx_notice}\n\n"
                        f"Would you like details on any of these alternatives?"
                    )
                else:
                    reply_text = (
                        f"No partner stores within 30 km of **{loc_label}** currently have verified in-store stock for this item. "
                        f"Standard warehouse shipping is available.\n\n{approx_notice}"
                    )

                SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', tools_executed)
                return {
                    'agent': 'sathi',
                    'status': 'out_of_stock_nearby',
                    'reply': reply_text,
                    'products': alts if alts else ([target_prod] if target_prod else []),
                    'cards': alts if alts else ([target_prod] if target_prod else []),
                    'nearbyStores': [],
                    'toolsExecuted': tools_executed
                }

        # -------------------------------------------------------------------
        # INTENT 9: GENERAL CATALOG SEARCH & RECOMMENDATION PIPELINE
        # -------------------------------------------------------------------
        tools_executed.append('search_products')
        search_res = tool_lib.search_products(query=query)
        matched_products = search_res.get('products', [])

        # Store in session conversation state
        SessionMemoryManager.set_recommendations(session_key, matched_products)

        reply_text = ""
        llm_info = {'provider': 'grounded-engine', 'model': 'local-deterministic'}

        if self.provider.is_configured and matched_products:
            compact_catalog = [
                {'name': p['name'], 'price': p['price'], 'rating': p['rating'], 'brand': p.get('brand', ''), 'inStock': p.get('stock', 0) > 0}
                for p in matched_products[:5]
            ]
            try:
                from ..langchain_module import get_discovery_lcel_chain
                chain = get_discovery_lcel_chain(temperature=0.2, max_tokens=300)
                out_text = chain.invoke({
                    'query': query,
                    'catalog_matches': json.dumps(compact_catalog)
                })
                if out_text and out_text.strip():
                    reply_text = out_text.strip()
                    llm_info = {'provider': 'langchain-lcel', 'model': self.provider.groq.model if self.provider.groq.is_configured else self.provider.gemini.model}
            except Exception as e:
                logger.warning("Discovery LangChain LCEL chain failed, falling back: %s", e)
                user_prompt = (
                    f"Customer Query: {query}\n\n"
                    f"Verified Catalog Matches:\n{json.dumps(compact_catalog)}\n\n"
                    f"Provide a friendly, concise 2-3 sentence overview in natural conversational English/Hinglish. Mention the top picks, price range, and encourage the customer to ask for details or add to cart."
                )
                llm_res = self.provider.generate(
                    system_instruction=DISCOVERY_SYSTEM_INSTRUCTION,
                    prompt=user_prompt,
                    temperature=0.2,
                    max_tokens=300
                )
                if llm_res.get('text'):
                    reply_text = llm_res['text']
                    llm_info = llm_res

        # Deterministic grounded fallback
        if not reply_text:
            safe_query = (query[:60] + '...') if len(query) > 60 else query
            safe_query = re.sub(r'[\r\n\t]+', ' ', safe_query).strip()
            safe_query = re.sub(r'(?i)(api[_-]?key|secret|password|token|bearer|drop\s+table|delete\s+all|ignore\s+all)', '[redacted]', safe_query)

            if matched_products:
                items_summary = []
                for idx, p in enumerate(matched_products):
                    disc = f" ({p.get('discount')}% off)" if p.get('discount') else ""
                    items_summary.append(f"{idx + 1}. **{p['name']}** — ₹{p['price']:,.0f}{disc} | ★{p.get('rating', 0)}")
                summary_block = "\n".join(items_summary)

                reply_text = (
                    f"Here are {len(matched_products)} verified product recommendations for \"{safe_query}\":\n\n"
                    f"{summary_block}\n\n"
                    f"💡 *Next step*: You can ask *'Which one is the cheapest?'*, *'Add the second one to my cart'*, or *'Compare the first and third products'*."
                )
            else:
                if '[redacted]' in safe_query:
                    reply_text = (
                        "I couldn't find any products matching your search criteria. "
                        "Try refining your search by product name or category (e.g. Laptops, Audio, Mobiles, Fashion)."
                    )
                else:
                    reply_text = (
                        f"I searched our product catalog for \"{safe_query}\", but did not find an exact match under those criteria. "
                        "Try refining your search by category (e.g. Laptops, Audio, Mobiles, Fashion) or adjusting your budget."
                    )

        SessionMemoryManager.add_turn(session_key, query, reply_text, 'sathi', tools_executed)

        return {
            'agent': 'sathi',
            'status': 'success',
            'reply': reply_text,
            'products': matched_products,
            'cards': matched_products,
            'recommendationListId': SessionMemoryManager.get_state(session_key).get('recommendation_list_id', ''),
            'orderedProductIds': [p['id'] for p in matched_products],
            'selectedProductId': matched_products[0]['id'] if matched_products else None,
            'toolsExecuted': tools_executed,
            'llmProvider': llm_info.get('provider', 'grounded-engine'),
            'suggestedActions': [
                'Which one is the cheapest?',
                'Add the first one to cart',
                'Compare top picks',
                'Check nearby store availability'
            ]
        }

    def run_discovery_agent(
        self,
        query: str,
        session_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_lat: Optional[float] = None,
        customer_lng: Optional[float] = None,
        cart_items: Optional[List[Dict[str, Any]]] = None,
        pincode: Optional[str] = None
    ) -> Dict[str, Any]:
        """Discovery agent adapter that delegates to the comprehensive Sathi engine."""
        res = self.run_sathi(
            query=query,
            session_id=session_id,
            customer_email=customer_email,
            cart_items=cart_items,
            customer_lat=customer_lat,
            customer_lng=customer_lng,
            pincode=pincode
        )
        res['agent'] = 'discovery'
        return res

    # -----------------------------------------------------------------------
    # AGENT B: CUSTOMER ENGAGEMENT & SUPPORT AGENT
    # -----------------------------------------------------------------------
    def run_customer_engagement_agent(
        self,
        query: str,
        cart_items: Optional[List[Dict[str, Any]]] = None,
        session_id: Optional[str] = None,
        customer_email: Optional[str] = None
    ) -> Dict[str, Any]:
        t0 = time.time()
        session_key = SessionMemoryManager.get_session_key(session_id, customer_email)
        tools_executed = []
        user_lower = query.lower()
        orders_payload = []
        tracking_payload = None

        # Determine explicit order ID from query if present
        order_id_match = re.search(r'\b(?:ord-ai-[a-f0-9]+|ord-\d{4}-\d{3,6}|[a-f0-9]{8}-[a-f0-9]{4})\b', query, re.I)
        target_order_id = order_id_match.group(0).upper() if order_id_match else None

        # 1. ORDER CANCELLATION INTENT (must take precedence over general order lookups)
        if any(w in user_lower for w in ['cancel', 'cancellation']):
            tools_executed.append('request_order_cancellation')
            if target_order_id:
                target_order = Order.objects.filter(id__iexact=target_order_id).first()
                if not target_order:
                    reply_text = f"I searched our records but could not find order **#{target_order_id}**. Please verify your order ID or check your active orders."
                    SessionMemoryManager.add_turn(session_key, query, reply_text, 'engagement', tools_executed)
                    return {
                        'agent': 'customer-engagement',
                        'status': 'error',
                        'reply': reply_text,
                        'toolsExecuted': tools_executed,
                        'suggestedActions': ['Track my orders', 'Return policy', 'Explore catalog products']
                    }
                # Check ownership if email provided
                if customer_email and target_order.customerEmail.lower() != customer_email.lower():
                    reply_text = f"Order **#{target_order.id}** belongs to another account. For security, you can only cancel orders placed under your own account ({customer_email})."
                    SessionMemoryManager.add_turn(session_key, query, reply_text, 'engagement', tools_executed)
                    return {
                        'agent': 'customer-engagement',
                        'status': 'unauthorized',
                        'reply': reply_text,
                        'toolsExecuted': tools_executed,
                        'suggestedActions': ['Track my orders', 'Explore catalog products']
                    }
                cancel_res = tool_lib.request_order_cancellation(target_order.id, reason="Customer requested cancellation via assistant", customer_email=customer_email or target_order.customerEmail)
                if cancel_res.get('success'):
                    reply_text = (
                        f"✅ **Order #{target_order.id} Cancelled Successfully**\n\n"
                        f"Your order has been cancelled. Any reserved stock has been released, and your refund of ₹{target_order.totalAmount:,.0f} has been initiated back to your original payment method."
                    )
                else:
                    reply_text = f"❌ Could not cancel order #{target_order.id}: {cancel_res.get('error', 'Order cannot be cancelled at this stage.')}"
                SessionMemoryManager.add_turn(session_key, query, reply_text, 'engagement', tools_executed)
                return {
                    'agent': 'customer-engagement',
                    'status': 'success' if cancel_res.get('success') else 'error',
                    'reply': reply_text,
                    'toolsExecuted': tools_executed,
                    'suggestedActions': ['Track my orders', 'Explore catalog products', 'Return policy']
                }
            else:
                if customer_email:
                    orders_res = tool_lib.get_my_orders(customer_email=customer_email, limit=3)
                    orders_payload = orders_res.get('orders', [])
                    tools_executed.append('get_my_orders')
                    if not orders_payload:
                        reply_text = "You do not have any active orders to cancel."
                        SessionMemoryManager.add_turn(session_key, query, reply_text, 'engagement', tools_executed)
                        return {
                            'agent': 'customer-engagement',
                            'status': 'success',
                            'reply': reply_text,
                            'toolsExecuted': tools_executed,
                            'suggestedActions': ['Explore catalog products', 'Return policy']
                        }
                    latest_order = orders_payload[0]
                    cancel_res = tool_lib.request_order_cancellation(latest_order['id'], reason="Customer requested cancellation via assistant", customer_email=customer_email)
                    if cancel_res.get('success'):
                        reply_text = (
                            f"✅ **Order #{latest_order['id']} Cancelled Successfully**\n\n"
                            f"Your order has been cancelled. Any reserved stock has been released, and your refund of ₹{latest_order['totalAmount']:,.0f} has been initiated back to your original payment method."
                        )
                    else:
                        reply_text = f"❌ Could not cancel order #{latest_order['id']}: {cancel_res.get('error', 'Order cannot be cancelled at this stage.')}"
                    SessionMemoryManager.add_turn(session_key, query, reply_text, 'engagement', tools_executed)
                    return {
                        'agent': 'customer-engagement',
                        'status': 'success' if cancel_res.get('success') else 'error',
                        'reply': reply_text,
                        'toolsExecuted': tools_executed,
                        'suggestedActions': ['Track my orders', 'Explore catalog products']
                    }
                else:
                    reply_text = (
                        "Please sign in with your AutoCart account to cancel an order, "
                        "or specify the order ID (e.g., `Order ORD-2026-XXXX cancel this order`)."
                    )
                    return {
                        'agent': 'customer-engagement',
                        'status': 'auth_required',
                        'reply': reply_text,
                        'toolsExecuted': tools_executed,
                        'suggestedActions': ['Log in to view my orders', 'Return policy']
                    }

        # 2. RETURN / REFUND / EXCHANGE INTENT
        elif any(w in user_lower for w in ['return', 'refund', 'exchange']):
            if target_order_id:
                ret_check = tool_lib.check_order_return_eligibility(target_order_id, customer_email or '')
                tools_executed.append('check_order_return_eligibility')
                if ret_check.get('eligible'):
                    reply_text = (
                        f"Order #{target_order_id} is **eligible** for return. "
                        f"Policy: {ret_check.get('conditions')} You have a 7-day return window from delivery date."
                    )
                else:
                    reply_text = f"Order #{target_order_id} is **not eligible** for return. Reason: {ret_check.get('reason', 'Policy condition not met')}."
                SessionMemoryManager.add_turn(session_key, query, reply_text, 'engagement', tools_executed)
                return {
                    'agent': 'customer-engagement',
                    'status': 'success',
                    'reply': reply_text,
                    'toolsExecuted': tools_executed,
                    'suggestedActions': ['Request return pickup', 'Track my orders', 'Speak with human agent']
                }

            if customer_email and any(w in user_lower for w in ['my order', 'return order']):
                orders_res = tool_lib.get_my_orders(customer_email=customer_email, limit=1)
                latest_order = (orders_res.get('orders') or [{}])[0]
                if latest_order.get('id'):
                    ret_check = tool_lib.check_order_return_eligibility(latest_order['id'], customer_email)
                    tools_executed.append('check_order_return_eligibility')
                    reply_text = (
                        f"Order #{latest_order['id']} (Placed on {latest_order.get('date')} for ₹{latest_order.get('totalAmount')}) "
                        f"is **{('eligible' if ret_check.get('eligible') else 'not eligible')}** for return. "
                        f"Policy: {ret_check.get('conditions')} You have a 7-day return window from delivery date."
                    )
                    return {
                        'agent': 'customer-engagement',
                        'status': 'success',
                        'reply': reply_text,
                        'toolsExecuted': tools_executed,
                        'suggestedActions': ['Request return pickup', 'Track my orders', 'Speak with human agent']
                    }

            policy = tool_lib.get_return_policy()
            tools_executed.append('get_return_policy')
            reply_text = (
                f"AutoCart Return & Refund Policy: We offer a **{policy['returnWindowDays']}-day return window** from delivery. "
                f"Items must be unused in original packaging. Refunds are credited to original payment within 5-7 business days."
            )
            return {
                'agent': 'customer-engagement',
                'status': 'success',
                'reply': reply_text,
                'toolsExecuted': tools_executed,
                'suggestedActions': ['Check my orders', 'Free shipping policy', 'Contact support']
            }

        # 3. SHIPPING & DELIVERY TIMELINE INQUIRY
        elif any(w in user_lower for w in ['shipping', 'delivery time', 'courier', 'charge', 'cost', 'how long is shipping']):
            ship_policy = tool_lib.get_shipping_policy()
            tools_executed.append('get_shipping_policy')
            reply_text = (
                f"AutoCart Delivery Timelines: Standard delivery takes **{ship_policy['standardDeliveryDays']}**. "
                f"Metro areas qualify for express 1-2 day delivery. Orders over ₹499 receive **Free Standard Delivery** "
                f"(₹40 delivery fee for smaller orders). All orders include real-time GPS tracking."
            )
            return {
                'agent': 'customer-engagement',
                'status': 'success',
                'reply': reply_text,
                'toolsExecuted': tools_executed,
                'suggestedActions': ['Track an order', 'Check cart total', 'Return policy']
            }

        # 4. ORDER TRACKING, STATUS & FULFILLMENT TIMELINE
        elif any(w in user_lower for w in ['order', 'track', 'status', 'delivery', 'package', 'where is', 'timeline', 'fulfillment']):
            # If explicit order ID provided
            if target_order_id:
                target_order = Order.objects.filter(id__iexact=target_order_id).first()
                if not target_order:
                    reply_text = f"I could not find order **#{target_order_id}** in our database. Please verify your order ID."
                    SessionMemoryManager.add_turn(session_key, query, reply_text, 'engagement', tools_executed)
                    return {
                        'agent': 'customer-engagement',
                        'status': 'error',
                        'reply': reply_text,
                        'toolsExecuted': tools_executed,
                        'suggestedActions': ['Track my orders', 'Contact support']
                    }
                if customer_email and target_order.customerEmail.lower() != customer_email.lower():
                    reply_text = f"Order **#{target_order.id}** is registered under another email. You can only view orders placed by your account."
                    SessionMemoryManager.add_turn(session_key, query, reply_text, 'engagement', tools_executed)
                    return {
                        'agent': 'customer-engagement',
                        'status': 'unauthorized',
                        'reply': reply_text,
                        'toolsExecuted': tools_executed,
                        'suggestedActions': ['Track my orders', 'Contact support']
                    }
                tracking_payload = tool_lib.get_order_fulfillment_tracking(target_order.id, customer_email or target_order.customerEmail)
                tools_executed.append('get_order_fulfillment_tracking')
                orders_payload = [{
                    'id': target_order.id, 'date': target_order.date, 'totalAmount': target_order.totalAmount,
                    'status': target_order.status, 'paymentStatus': target_order.paymentStatus
                }]
                status_desc = f"Order **#{target_order.id}** ({target_order.date}) is **{target_order.status}** (Payment: {target_order.paymentStatus})."
                if tracking_payload and not tracking_payload.get('error'):
                    status_desc += f" Current tracking: **{tracking_payload.get('currentStatus')}** via {tracking_payload.get('deliveryPartner')}."
                reply_text = status_desc
                SessionMemoryManager.add_turn(session_key, query, reply_text, 'engagement', tools_executed)
                return {
                    'agent': 'customer-engagement',
                    'status': 'success',
                    'reply': reply_text,
                    'orders': orders_payload,
                    'tracking': tracking_payload,
                    'toolsExecuted': tools_executed,
                    'suggestedActions': ['Track another order', 'Return policy']
                }

            if customer_email:
                orders_res = tool_lib.get_my_orders(customer_email=customer_email, limit=3)
                orders_payload = orders_res.get('orders', [])
                tools_executed.append('get_my_orders')

                if orders_payload:
                    latest_order_id = orders_payload[0]['id']
                    tracking_payload = tool_lib.get_order_fulfillment_tracking(latest_order_id, customer_email)
                    tools_executed.append('get_order_fulfillment_tracking')
                    latest = orders_payload[0]
                    status_desc = f"Your latest order **#{latest['id']}** ({latest.get('date')}) is **{latest.get('status')}** (Payment: {latest.get('paymentStatus')})."
                    if tracking_payload and not tracking_payload.get('error'):
                        status_desc += f" Current tracking: **{tracking_payload.get('currentStatus')}** via {tracking_payload.get('deliveryPartner')}."
                    reply_text = status_desc
                else:
                    reply_text = "You do not have any active orders yet. Once you place an order, you can view its fulfillment timeline and live GPS tracking here."

                SessionMemoryManager.add_turn(session_key, query, reply_text, 'engagement', tools_executed)
                return {
                    'agent': 'customer-engagement',
                    'status': 'success',
                    'reply': reply_text,
                    'orders': orders_payload,
                    'tracking': tracking_payload,
                    'toolsExecuted': tools_executed,
                    'suggestedActions': ['Browse products', 'Return & cancellation policy'] if not orders_payload else ['Track my order', 'Return & cancellation policy']
                }
            else:
                reply_text = (
                    "To securely retrieve your order records and live tracking details, please log in with your AutoCart account. "
                    "Alternatively, provide your registered order ID (e.g., ORD-2026-XXXX)."
                )
                return {
                    'agent': 'customer-engagement',
                    'status': 'auth_required',
                    'reply': reply_text,
                    'toolsExecuted': [],
                    'suggestedActions': ['Log in to view my orders', 'Check return policy', 'Shipping timelines']
                }

        # Cart inquiry fallback
        cart_summary = tool_lib.get_cart_summary(cart_items or [])
        tools_executed.append('get_cart_summary')

        if orders_payload:
            latest = orders_payload[0]
            status_desc = f"Your latest order **#{latest['id']}** ({latest.get('date')}) is **{latest.get('status')}** (Payment: {latest.get('paymentStatus')})."
            if tracking_payload:
                status_desc += f" Current tracking: **{tracking_payload.get('currentStatus')}** via {tracking_payload.get('deliveryPartner')}."
            reply_text = status_desc
        else:
            reply_text = (
                f"Hello! Your current shopping cart has an active subtotal of **₹{cart_summary['subtotal']:,.2f}**. "
                f"{('You qualify for Free Shipping!' if cart_summary['freeShippingEligible'] else 'Add ₹' + str(round(max(0, 500 - cart_summary['subtotal']), 2)) + ' more to qualify for Free Shipping.')} "
                "How else can I assist you with your orders or policies today?"
            )

        SessionMemoryManager.add_turn(session_key, query, reply_text, 'engagement', tools_executed)

        return {
            'agent': 'customer-engagement',
            'status': 'success',
            'reply': reply_text,
            'orders': orders_payload,
            'tracking': tracking_payload,
            'toolsExecuted': tools_executed,
            'suggestedActions': ['Track my order', 'Return & cancellation policy', 'Explore catalog products']
        }

    # -----------------------------------------------------------------------
    # AGENT C: LOCATION & FULFILLMENT AGENT
    # -----------------------------------------------------------------------
    def run_location_fulfillment_agent(
        self,
        product_id: str,
        quantity: int = 1,
        store_id: Optional[str] = None,
        customer_lat: float = 12.9716,
        customer_lng: float = 77.5946,
        user_email: str = 'customer@example.com'
    ) -> Dict[str, Any]:
        """
        Coordinates nearby store discovery, live inventory verification, and stock reservation.
        """
        quote = tool_lib.calculate_fulfillment_quote(
            product_id=product_id,
            quantity=quantity,
            store_id=store_id,
            lat=customer_lat,
            lng=customer_lng
        )

        stores_res = tool_lib.find_nearby_stores_for_product(
            product_id=product_id,
            lat=customer_lat,
            lng=customer_lng,
            radius_km=25.0,
            required_quantity=quantity
        )

        return {
            'agent': 'fulfillment',
            'status': 'success',
            'quote': quote,
            'nearbyEligibleStores': stores_res.get('stores', []),
            'selectedStoreId': store_id or (stores_res.get('stores', [{}])[0].get('storeId')),
            'requiresCustomerConfirmation': True,
            'confirmationPrompt': (
                f"Confirm reservation for {quantity}x {quote.get('productName')} at "
                f"{quote.get('storeName')} for total of ₹{quote.get('totalAmount')}?"
            )
        }

    # -----------------------------------------------------------------------
    # AGENT D: SELLER ONBOARDING & VERIFICATION AGENT
    # -----------------------------------------------------------------------
    def run_seller_onboarding_agent(
        self,
        application_data: Dict[str, Any],
        user_role: str = 'CUSTOMER',
        user_email: str = ''
    ) -> Dict[str, Any]:
        """
        Evaluates seller documents, runs OCR extraction, validates tax IDs, and produces a structured compliance score.
        """
        from ..ocr_service import DocumentOCRService

        # Check if a real application ID was provided
        app_id = application_data.get('id') or application_data.get('applicationId')
        app = None
        if app_id:
            try:
                from ..models import SellerApplication
                app = SellerApplication.objects.filter(id=app_id).first()
            except Exception:
                app = None

        if app:
            from .. import seller_docs
            docs = list(app.documents.all())
            comparison = seller_docs.compare_application(app, docs)
            decision = seller_docs.decide_status(app, docs, comparison)
            val_res = tool_lib.validate_seller_application({
                'name': app.applicantName,
                'companyName': app.companyName,
                'email': app.email,
                'phone': app.phone,
                'city': app.city,
                'businessType': app.businessType,
                'productCategories': app.productCategories or [],
                'gstin': app.gstin,
                'pan': app.pan,
                'pincode': app.pincode,
                'storeLatitude': app.storeLatitude,
                'storeLongitude': app.storeLongitude,
                'plannedProducts': app.plannedProducts or [],
            })
            have = {d.docType for d in docs}
            missing_docs = [t for t in seller_docs.REQUIRED_DOC_TYPES if t not in have]
            mismatches = comparison.get('mismatches', 0)
            risk_score = comparison.get('riskScore', 0)
            risk_cat = comparison.get('riskCategory', 'Low')

            docs_summary = [
                {
                    'docType': d.docType,
                    'fileName': d.fileName,
                    'ocrStatus': d.ocrStatus,
                    'confidence': d.confidence,
                    'extractedFields': d.extractedFields or {},
                    'warnings': d.warnings or []
                }
                for d in docs
            ]

            status_label = (
                'Ready for admin review' if not missing_docs and mismatches == 0
                else ('Needs manual review' if mismatches > 0 or any(d.ocrStatus == 'UNREADABLE' for d in docs)
                      else 'Waiting for required documents')
            )

            reply_summary = (
                f"📋 **Agent D Verification Assessment for {app.companyName}** (`{app.id}`):\n\n"
                f"• **Risk Index**: **{risk_score}/100** ({risk_cat} Risk)\n"
                f"• **Preliminary Status**: `{status_label}`\n"
                f"• **Documents Uploaded**: {len(docs)} document(s) ({', '.join(have) if have else 'None'})\n"
                f"• **Missing Required Documents**: {', '.join(missing_docs) if missing_docs else 'None (All required KYC documents in order)'}\n"
                f"• **Field Mismatches**: {mismatches}\n"
                f"• **Products Listed**: {len(app.plannedProducts or [])} product(s)\n\n"
                f"💡 *Human Administrator Decision Required*: You can review and approve this application in the Seller Onboarding workspace."
            )

            return {
                'agent': 'seller-onboarding',
                'status': 'success',
                'applicationId': app.id,
                'riskScore': risk_score,
                'riskCategory': risk_cat,
                'preliminaryStatus': status_label,
                'missingFields': missing_docs,
                'checklist': val_res.get('checklist', []),
                'discrepancies': [c for c in comparison.get('checks', []) if c.get('status') == 'mismatch'],
                'verifiedFacts': [c['label'] for c in comparison.get('checks', []) if c.get('status') == 'match'],
                'documentsSummary': docs_summary,
                'productsCount': len(app.plannedProducts or []),
                'reply': reply_summary
            }

        # 1. Fallback for raw dictionary evaluation
        val_res = tool_lib.validate_seller_application(application_data)
        
        # 2. Cross check with simulated OCR extraction on submitted GSTIN/PAN
        gstin = application_data.get('gstin', '')
        raw_doc_text = f"Government of India Tax Registration Certificate GSTIN: {gstin} Legal Name: {application_data.get('companyName')}"
        ocr_res = DocumentOCRService.extract_document_entities(raw_doc_text, 'GST_CERTIFICATE')
        cross_res = DocumentOCRService.cross_validate_application(application_data, ocr_res)

        final_risk = max(val_res['riskScore'], cross_res['riskScore'])
        status_label = (
            'Ready for review' if final_risk <= 30 and not val_res['missingFields']
            else ('Needs verification' if final_risk <= 55 else 'High verification required')
        )

        reply_summary = (
            f"Agent D Verification Assessment for **{application_data.get('companyName', 'Applicant')}**:\n\n"
            f"• **Risk Index**: {final_risk}/100 ({cross_res['riskCategory']} Risk)\n"
            f"• **Preliminary Status**: {status_label}\n"
            f"• **OCR Confidence**: {ocr_res['confidenceScore']}%\n"
            f"• **Checklist Status**: {sum(1 for c in val_res['checklist'] if c['complete'])}/{len(val_res['checklist'])} items verified."
        )

        return {
            'agent': 'seller-onboarding',
            'status': 'success',
            'riskScore': final_risk,
            'riskCategory': cross_res['riskCategory'],
            'preliminaryStatus': status_label,
            'missingFields': val_res['missingFields'],
            'checklist': val_res['checklist'],
            'ocrExtracted': ocr_res,
            'discrepancies': cross_res['discrepancies'],
            'verifiedFacts': cross_res['verifiedFacts'],
            'nextSteps': [
                'Ensure all required identity, trade, and tax certificates are clearly uploaded',
                'Verify Indian registered business address matches GST state code',
                'Authorized human administrator approval required before marketplace activation'
            ],
            'reply': reply_summary
        }

    # -----------------------------------------------------------------------
    # AGENT E: SELLER BUSINESS ASSISTANT AGENT
    # -----------------------------------------------------------------------
    def run_seller_business_assistant(
        self,
        prompt: str,
        seller_id: str,
        title: Optional[str] = None,
        category: Optional[str] = None,
        raw_specs: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Assists registered sellers with listing drafting, competitive price benchmarks, and low-stock alerts.
        """
        p_lower = prompt.lower()
        tools_executed = []

        if any(w in p_lower for w in ['list', 'draft', 'create product', 'description', 'title']):
            listing_res = tool_lib.generate_seller_product_listing(
                title=title or 'Smart Device',
                category=category or 'Electronics',
                raw_specs=raw_specs,
                seller_name='Seller Partner'
            )
            tools_executed.append('generate_seller_product_listing')
            reply_text = (
                f"I drafted an optimized product listing for **{listing_res['suggestedTitle']}** in category **{listing_res['category']}**.\n\n"
                f"• Recommended Price: **₹{listing_res['recommendedPrice']:,.2f}** (MSRP: ₹{listing_res['suggestedMSRP']:,.2f})\n"
                f"• Description: {listing_res['draftDescription']}\n\n"
                f"{listing_res['requiresConfirmation']}"
            )
            return {
                'agent': 'seller_assistant',
                'status': 'success',
                'reply': reply_text,
                'listingDraft': listing_res,
                'toolsExecuted': tools_executed
            }

        # Inventory and pricing health check
        inv_res = tool_lib.analyze_seller_inventory_and_pricing(seller_id)
        tools_executed.append('analyze_seller_inventory_and_pricing')
        reply_text = (
            f"Seller Inventory Analysis: Across {inv_res['storesCount']} fulfillment location(s), "
            f"you have **{inv_res['lowStockAlertCount']} item(s) running low on stock** (≤5 units remaining). "
            f"Recommended priority: Restock fast-moving SKUs at Indiranagar and Koramangala hubs to maintain hyperlocal eligibility."
        )
        return {
            'agent': 'seller_assistant',
            'status': 'success',
            'reply': reply_text,
            'inventoryHealth': inv_res,
            'toolsExecuted': tools_executed
        }

    # -----------------------------------------------------------------------
    # AGENT F: ADMIN MARKETPLACE ASSISTANT AGENT
    # -----------------------------------------------------------------------
    def run_admin_assistance_agent(
        self,
        prompt: str,
        user_role: str = 'ADMIN',
        application_id: Optional[str] = None,
        user_email: Optional[str] = None,
        confirmed: bool = False,
        action: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Helps marketplace administrators audit multi-vendor applications, highlight compliance risks,
        manage pending/approved queues, and safely execute approved workflows with human confirmation.
        """
        if user_role not in ('ADMIN', 'STAFF'):
            return {
                'agent': 'admin_assistant',
                'status': 'error',
                'error': 'Access denied: Admin authorization required.',
                'reply': 'Access denied. You must be an authenticated administrator or staff member to query onboarding operations.'
            }

        p_lower = (prompt or '').strip().lower()
        tools_executed = []

        # Extract potential application ID from prompt if not explicitly provided
        extracted_app_id = application_id
        if not extracted_app_id:
            id_match = re.search(r'\b(app-[a-zA-Z0-9_-]+)\b', prompt, re.I)
            if id_match:
                extracted_app_id = id_match.group(1)
            else:
                num_match = re.search(r'\b(?:application|app)\s*#?\s*([0-9]+)\b', prompt, re.I)
                if num_match:
                    extracted_app_id = num_match.group(1)

        # -------------------------------------------------------------------
        # WORKFLOW A: REMOVE SELLERS WITH RISK SCORE > 50
        # -------------------------------------------------------------------
        if action == 'REMOVE_HIGH_RISK_SELLERS' or (
            any(w in p_lower for w in ['remove', 'suspend', 'deactivate', 'delete'])
            and 'risk' in p_lower
            and ('50' in p_lower or 'more than' in p_lower or '>' in p_lower)
        ):
            tools_executed.append('filter_high_risk_sellers')
            # Strictly riskScore > 50
            high_risk_apps = list(SellerApplication.objects.filter(riskScore__gt=50).exclude(status__in=['REJECTED', 'SUSPENDED']))

            is_confirmed = confirmed or any(p_lower.startswith(w) for w in ['yes', 'confirm', 'proceed', 'confirmed']) or ('confirm' in p_lower and 'remove' in p_lower)

            affected = [{
                'id': a.id,
                'companyName': a.companyName or a.storeName,
                'applicantName': a.applicantName,
                'city': a.city or 'Kalyan',
                'riskScore': a.riskScore,
                'riskCategory': a.riskCategory,
                'status': a.status,
            } for a in high_risk_apps]

            if not is_confirmed:
                lines = [f"• {a['companyName']} ({a['id']}): Risk {a['riskScore']}/100 ({a['riskCategory']}) | Current Status: {a['status']}" for a in affected]
                lines_text = "\n".join(lines) if lines else "No active or pending sellers currently exceed a risk score of 50."
                reply_text = (
                    f"Found {len(affected)} seller(s) with risk score strictly greater than 50 (risk_score > 50):\n\n"
                    f"{lines_text}\n\n"
                    f"Administrative confirmation required: Executing this action will suspend approved stores and reject pending applications for all {len(affected)} flagged seller(s).\n\n"
                    f"Please click 'Confirm Execution' or reply 'confirm remove high risk sellers' to proceed."
                ) if affected else "No active or pending sellers found with risk score strictly greater than 50."

                return {
                    'agent': 'admin_assistant',
                    'status': 'confirmation_required' if affected else 'success',
                    'requiresConfirmation': bool(affected),
                    'action': 'REMOVE_HIGH_RISK_SELLERS',
                    'threshold': 50,
                    'affectedCount': len(affected),
                    'affectedApplications': affected,
                    'applications': affected,
                    'reply': reply_text,
                    'toolsExecuted': tools_executed
                }

            # Confirmed execution: suspend or reject
            for a in high_risk_apps:
                old_status = a.status
                new_status = 'SUSPENDED' if old_status == 'APPROVED' else 'REJECTED'
                a.status = new_status
                a.save()
                if old_status == 'APPROVED':
                    Store.objects.filter(id=f"store-{a.id}").update(operatingStatus='Closed')
                    Seller.objects.filter(id=f"sel-{a.id}").update(status='Suspended')
                SellerApplicationAudit.objects.create(
                    id=f"aud-{uuid.uuid4().hex[:8]}",
                    application=a,
                    fromStatus=old_status,
                    toStatus=new_status,
                    action='SUSPEND' if new_status == 'SUSPENDED' else 'REJECT',
                    performedBy=user_email or 'admin@autocart.com',
                    reason='Automated high-risk removal: risk score > 50 confirmed by administrator'
                )

            return {
                'agent': 'admin_assistant',
                'status': 'success',
                'reply': f"Successfully removed/suspended {len(affected)} high-risk seller(s) with risk score strictly greater than 50. All associated seller accounts and storefront listings have been closed.",
                'affectedCount': len(affected),
                'affectedApplications': affected,
                'applications': affected,
                'toolsExecuted': tools_executed + ['execute_remove_high_risk_sellers']
            }

        # -------------------------------------------------------------------
        # WORKFLOW B: APPROVE / REJECT SELLER (WITH ENTITY RESOLUTION & CONFIRMATION)
        # -------------------------------------------------------------------
        is_approval_intent = (
            any(p_lower.startswith(w) for w in ['approve ', 'approve', 'accept ']) or
            ('approve' in p_lower and not any(w in p_lower for w in ['before approve', 'review before', 'checklist', 'what should']))
        ) and not ('show approved' in p_lower or 'all approved' in p_lower)

        is_rejection_intent = (
            any(p_lower.startswith(w) for w in ['reject ', 'reject', 'decline ']) or
            ('reject' in p_lower and not ('show rejected' in p_lower or 'all rejected' in p_lower))
        )

        if action in ('APPROVE', 'REJECT') or is_approval_intent or is_rejection_intent:
            target_action = action if action in ('APPROVE', 'REJECT') else ('APPROVE' if is_approval_intent else 'REJECT')
            tools_executed.append(f"resolve_{target_action.lower()}_request")
            from ..seller_views import _activate_seller

            target_app = None
            if extracted_app_id:
                target_app = SellerApplication.objects.filter(id=extracted_app_id).first()

            if not target_app:
                # Clean prompt to locate business name
                clean_target = re.sub(r'^(?:please\s+)?(?:confirm\s+)?(?:approve|reject|decline)\s+(?:application|seller|store\s+)?', '', p_lower).strip()
                clean_target = re.sub(r'\s+(?:application|seller|store)$', '', clean_target).strip()
                if clean_target:
                    target_app = SellerApplication.objects.filter(
                        Q(companyName__icontains=clean_target) |
                        Q(storeName__icontains=clean_target) |
                        Q(applicantName__icontains=clean_target)
                    ).first()

            if not target_app and 'amart' in p_lower:
                target_app = SellerApplication.objects.filter(companyName__icontains='amart').first()

            if not target_app:
                # If target is still missing, fallback to highest pending application if any
                target_app = SellerApplication.objects.filter(status__in=['PENDING_ADMIN_APPROVAL', 'NEEDS_MANUAL_REVIEW']).first()

            if not target_app:
                return {
                    'agent': 'admin_assistant',
                    'status': 'not_found',
                    'reply': f"Could not find a seller application matching '{prompt}'. Please provide a valid application ID or registered company name.",
                    'toolsExecuted': tools_executed
                }

            is_confirmed = confirmed or any(p_lower.startswith(w) for w in ['yes', 'confirm', 'proceed', 'confirmed']) or ('confirm' in p_lower and ('approve' in p_lower or 'reject' in p_lower))

            if not is_confirmed:
                consequence = (
                    "This will approve the seller, create their live marketplace store, and allow active catalog sales."
                    if target_action == 'APPROVE' else
                    "This will reject the seller application and prevent live marketplace onboarding."
                )
                return {
                    'agent': 'admin_assistant',
                    'status': 'confirmation_required',
                    'requiresConfirmation': True,
                    'action': target_action,
                    'applicationId': target_app.id,
                    'companyName': target_app.companyName,
                    'riskScore': target_app.riskScore,
                    'riskCategory': target_app.riskCategory,
                    'reply': (
                        f"Administrative confirmation required: You are requesting to {target_action.lower()} application for {target_app.companyName} ({target_app.id}).\n\n"
                        f"• Applicant: {target_app.applicantName}\n"
                        f"• Store Location: {target_app.city}, {target_app.pincode}\n"
                        f"• Deterministic Risk Score: {target_app.riskScore}/100 ({target_app.riskCategory} Risk)\n"
                        f"• Current Status: {target_app.status}\n\n"
                        f"Action consequence: {consequence}\n\n"
                        f"Please click 'Confirm Execution' below or reply 'confirm {target_action.lower()} {target_app.id}' to execute this change in the database."
                    ),
                    'applications': [{
                        'id': target_app.id,
                        'companyName': target_app.companyName,
                        'applicantName': target_app.applicantName,
                        'city': target_app.city,
                        'status': target_app.status,
                        'riskScore': target_app.riskScore,
                        'riskCategory': target_app.riskCategory
                    }],
                    'toolsExecuted': tools_executed
                }

            # Confirmed execution
            old_status = target_app.status
            if target_action == 'APPROVE':
                target_app.status = 'APPROVED'
                target_app.save()
                _activate_seller(target_app, user_email or 'admin@autocart.com')
                SellerApplicationAudit.objects.create(
                    id=f"aud-{uuid.uuid4().hex[:8]}",
                    application=target_app,
                    fromStatus=old_status,
                    toStatus='APPROVED',
                    action='APPROVE',
                    performedBy=user_email or 'admin@autocart.com',
                    reason='Approved by administrator via Admin AI Risk Assistant with explicit human confirmation'
                )
                reply_msg = f"Successfully approved {target_app.companyName} ({target_app.id}). The seller and store are now live and active on the marketplace."
            else:
                target_app.status = 'REJECTED'
                target_app.save()
                SellerApplicationAudit.objects.create(
                    id=f"aud-{uuid.uuid4().hex[:8]}",
                    application=target_app,
                    fromStatus=old_status,
                    toStatus='REJECTED',
                    action='REJECT',
                    performedBy=user_email or 'admin@autocart.com',
                    reason='Rejected by administrator via Admin AI Risk Assistant with explicit human confirmation'
                )
                reply_msg = f"Successfully rejected application for {target_app.companyName} ({target_app.id}). Status has been updated in the database."

            return {
                'agent': 'admin_assistant',
                'status': 'success',
                'reply': reply_msg,
                'applicationId': target_app.id,
                'actionExecuted': target_action,
                'applications': [{
                    'id': target_app.id,
                    'companyName': target_app.companyName,
                    'applicantName': target_app.applicantName,
                    'city': target_app.city,
                    'status': target_app.status,
                    'riskScore': target_app.riskScore,
                    'riskCategory': target_app.riskCategory
                }],
                'toolsExecuted': tools_executed + [f"execute_{target_action.lower()}"]
            }

        # -------------------------------------------------------------------
        # WORKFLOW C: SHOW ALL APPROVED SELLERS
        # -------------------------------------------------------------------
        if any(w in p_lower for w in ['approved sellers', 'approved applications', 'all approved', 'show approved', 'active sellers']):
            tools_executed.append('list_approved_sellers')
            approved_apps = list(SellerApplication.objects.filter(status='APPROVED').order_by('-createdAt'))
            app_rows = [{
                'id': a.id,
                'companyName': a.companyName or a.storeName,
                'applicantName': a.applicantName,
                'city': a.city or 'Kalyan',
                'status': a.status,
                'riskScore': a.riskScore,
                'riskCategory': a.riskCategory,
            } for a in approved_apps]

            if app_rows:
                lines = [f"• {a['companyName']} ({a['id']}): {a['applicantName']} · {a['city']} | Risk: {a['riskScore']}/100 ({a['riskCategory']})" for a in app_rows]
                reply_text = f"Currently monitoring {len(app_rows)} approved and active seller(s) on the marketplace:\n\n" + "\n".join(lines)
            else:
                reply_text = "No approved sellers found in the system yet."

            return {
                'agent': 'admin_assistant',
                'status': 'success',
                'reply': reply_text,
                'applications': app_rows,
                'toolsExecuted': tools_executed
            }

        # -------------------------------------------------------------------
        # WORKFLOW D: SHOW REJECTED APPLICATIONS
        # -------------------------------------------------------------------
        if any(w in p_lower for w in ['rejected applications', 'rejected sellers', 'show rejected', 'all rejected', 'list rejected']):
            tools_executed.append('list_rejected_applications')
            rejected_apps = list(SellerApplication.objects.filter(status='REJECTED').order_by('-createdAt'))
            app_rows = [{
                'id': a.id,
                'companyName': a.companyName or a.storeName,
                'applicantName': a.applicantName,
                'city': a.city or 'Kalyan',
                'status': a.status,
                'riskScore': a.riskScore,
                'riskCategory': a.riskCategory,
            } for a in rejected_apps]

            if app_rows:
                lines = [f"• {a['companyName']} ({a['id']}): {a['applicantName']} · {a['city']} | Risk: {a['riskScore']}/100" for a in app_rows]
                reply_text = f"Found {len(app_rows)} rejected seller application(s):\n\n" + "\n".join(lines)
            else:
                reply_text = "No rejected seller applications found in the database."

            return {
                'agent': 'admin_assistant',
                'status': 'success',
                'reply': reply_text,
                'applications': app_rows,
                'toolsExecuted': tools_executed
            }

        # -------------------------------------------------------------------
        # WORKFLOW E: FIND ALL PENDING APPLICATIONS (INTERACTIVE CARDS)
        # -------------------------------------------------------------------
        if any(w in p_lower for w in ['pending', 'waiting for review', 'summarize all', 'all applications', 'find all pending', 'find pending']):
            tools_executed.append('summarize_pending_applications')
            pending_apps = list(SellerApplication.objects.filter(status__in=['PENDING_ADMIN_APPROVAL', 'NEEDS_MANUAL_REVIEW', 'DRAFT']).order_by('-createdAt'))
            if not pending_apps:
                pending_apps = list(SellerApplication.objects.exclude(status__in=['APPROVED', 'REJECTED', 'SUSPENDED']).order_by('-createdAt'))

            app_rows = []
            for a in pending_apps:
                docs = list(a.documents.all())
                req_count = sum(1 for d in docs if d.docType in ('AADHAAR', 'PAN') and d.ocrStatus != 'REJECTED')
                app_rows.append({
                    'id': a.id,
                    'companyName': a.companyName or a.storeName,
                    'applicantName': a.applicantName,
                    'city': a.city or 'Kalyan',
                    'status': a.status,
                    'riskScore': a.riskScore,
                    'riskCategory': a.riskCategory,
                    'documentCount': len(docs),
                    'requiredDocumentCount': req_count,
                    'totalRequiredDocuments': 2
                })

            if app_rows:
                lines = [f"• {a['companyName']} ({a['id']}): {a['applicantName']} · {a['city']} | Status: {a['status']} | Risk: {a['riskScore']}/100 ({a['riskCategory']})" for a in app_rows]
                reply_text = (
                    f"Found {len(app_rows)} pending seller application(s) awaiting administrative review:\n\n" +
                    "\n".join(lines) +
                    "\n\nClick on any interactive application card below to open the complete verification profile and inspect documents."
                )
            else:
                reply_text = "There are currently no pending seller applications awaiting review."

            return {
                'agent': 'admin_assistant',
                'status': 'success',
                'reply': reply_text,
                'applications': app_rows,
                'pendingSummary': {'pendingCount': len(app_rows), 'applications': app_rows},
                'toolsExecuted': tools_executed
            }

        # 1. EXPLAIN RISK SCORE
        if any(w in p_lower for w in ['explain', 'why is the risk', 'risk score', 'risk breakdown', 'risk factor']) and ('risk' in p_lower or 'score' in p_lower):
            if not extracted_app_id:
                # Look for the highest risk pending application
                apps = tool_lib.summarize_pending_applications(user_role).get('applications', [])
                if apps:
                    extracted_app_id = apps[0]['id']

            if not extracted_app_id:
                return {
                    'agent': 'admin_assistant',
                    'status': 'clarification',
                    'reply': "Please specify an application ID (e.g. 'Explain the risk score for application app-123') to inspect its risk calculation."
                }

            tools_executed.append('explain_application_risk')
            risk_res = tool_lib.explain_application_risk(extracted_app_id, user_role)
            if not risk_res.get('found'):
                return {
                    'agent': 'admin_assistant',
                    'status': 'not_found',
                    'reply': risk_res.get('error', f"Application '{extracted_app_id}' was not found in the database. Please verify the application ID."),
                    'toolsExecuted': tools_executed
                }

            factors_text = "\n".join([f"• **{f['factor']}** (+{f['points']} pts): {f['description']}" for f in risk_res['contributingFactors']]) if risk_res['contributingFactors'] else "• None (Clean profile, low risk baseline)."
            discrepancies_text = "\n".join([f"• {d['detail']}" for d in risk_res['validationDiscrepancies']]) if risk_res['validationDiscrepancies'] else "• No field discrepancies found."
            facts_text = "\n".join([f"• {fact}" for fact in risk_res['verifiedFacts'][:4]]) if risk_res['verifiedFacts'] else "• Verification in progress."

            reply_text = (
                f"📋 **Risk Assessment for {risk_res['companyName']}** (`{risk_res['applicationId']}`):\n\n"
                f"• **Deterministic Score**: **{risk_res['riskScore']}/100** ({risk_res['riskCategory']} Risk) [Version {risk_res['scoringVersion']}]\n"
                f"• **Recommended Action**: `{risk_res['recommendedAction']}`\n\n"
                f"**Contributing Risk Factors**:\n{factors_text}\n\n"
                f"**Validation Discrepancies**:\n{discrepancies_text}\n\n"
                f"**Verified Facts**:\n{facts_text}\n\n"
                f"💡 *Human Administrator Decision Required*: You can approve or reject this application in the Seller Onboarding workspace."
            )
            return {
                'agent': 'admin_assistant',
                'status': 'success',
                'reply': reply_text,
                'riskAnalysis': risk_res,
                'toolsExecuted': tools_executed
            }

        # 2. REVIEW CHECKLIST BEFORE APPROVING
        if any(w in p_lower for w in ['before approving', 'what should i review', 'what to review', 'review checklist', 'checklist before approve', 'check before approving']):
            if not extracted_app_id:
                apps = tool_lib.summarize_pending_applications(user_role).get('applications', [])
                if apps:
                    extracted_app_id = apps[0]['id']
            if not extracted_app_id:
                return {
                    'agent': 'admin_assistant',
                    'status': 'clarification',
                    'reply': "Please specify an application ID (e.g. 'What should I review before approving application app-123?') to inspect its review checklist."
                }
            tools_executed.append('explain_application_risk')
            risk_res = tool_lib.explain_application_risk(extracted_app_id, user_role)
            if not risk_res.get('found'):
                return {
                    'agent': 'admin_assistant',
                    'status': 'not_found',
                    'reply': risk_res.get('error', f"Application '{extracted_app_id}' was not found in the database."),
                    'toolsExecuted': tools_executed
                }
            reply_text = (
                f"📋 **Mandatory Review Checklist for {risk_res['companyName']}** (`{risk_res['applicationId']}`):\n\n"
                f"Before approving this application, confirm the following items:\n"
                f"1. **Aadhaar Document**: Verify it is a masked copy with only the last 4 digits visible. Check applicant legal name matches.\n"
                f"2. **PAN Card**: Verify the 10-character PAN number and legal entity name correspond with application records.\n"
                f"3. **Store Location**: Ensure the store latitude and longitude are pinned on the map within Mumbai/MMR.\n"
                f"4. **Cross-Document Consistency**: Check validation checks (currently {len(risk_res.get('validationDiscrepancies', []))} discrepancy/discrepancies found).\n"
                f"5. **Product & Stock Listings**: Inspect initial catalog entries and stock units.\n\n"
                f"• **Deterministic Score**: **{risk_res['riskScore']}/100** ({risk_res['riskCategory']} Risk) [v{risk_res['scoringVersion']}]\n"
                f"• **Recommended Action**: `{risk_res['recommendedAction']}`\n\n"
                f"⚖️ *Human Authority Notice*: The AI assistant provides evidence and advisory scoring only. Final approval or rejection rests entirely with you as an authorized administrator."
            )
            return {
                'agent': 'admin_assistant',
                'status': 'success',
                'reply': reply_text,
                'checklistReview': risk_res,
                'toolsExecuted': tools_executed
            }

        # 3. VALIDATION DISCREPANCIES
        if any(w in p_lower for w in ['discrepanc', 'mismatch', 'conflict', 'inconsisten']):
            tools_executed.append('get_validation_discrepancies')
            disc_res = tool_lib.get_validation_discrepancies(extracted_app_id, user_role)
            if extracted_app_id and not disc_res.get('found', True):
                return {
                    'agent': 'admin_assistant',
                    'status': 'not_found',
                    'reply': disc_res.get('error', f"Application '{extracted_app_id}' was not found."),
                    'toolsExecuted': tools_executed
                }

            if extracted_app_id:
                disc_list = disc_res.get('discrepancies', [])
                if disc_list:
                    lines = [f"• **{d['label']}**: {d['detail']}" for d in disc_list]
                    reply_text = f"Found **{len(disc_list)} discrepancy/discrepancies** for **{disc_res['companyName']}**:\n\n" + "\n".join(lines)
                else:
                    reply_text = f"No discrepancies found for **{disc_res['companyName']}**. Form entries match OCR document readings."
            else:
                apps_with_disc = disc_res.get('applicationsWithDiscrepancies', [])
                if apps_with_disc:
                    lines = [f"• **{a['companyName']}** (`{a['id']}`): {a['count']} mismatch(es)" for a in apps_with_disc]
                    reply_text = f"There are **{len(apps_with_disc)} application(s) with cross-document discrepancies**:\n\n" + "\n".join(lines)
                else:
                    reply_text = "All pending seller applications have zero cross-document discrepancies."

            return {
                'agent': 'admin_assistant',
                'status': 'success',
                'reply': reply_text,
                'discrepancies': disc_res,
                'toolsExecuted': tools_executed
            }

        # 3. MISSING DOCUMENTS
        if any(w in p_lower for w in ['missing doc', 'missing document', 'document missing', 'without doc', 'incomplete doc']):
            tools_executed.append('get_applications_with_missing_docs')
            missing_res = tool_lib.get_applications_with_missing_docs(user_role)
            flagged = missing_res.get('applications', [])
            if flagged:
                lines = [f"• **{a['companyName']}** (`{a['id']}`): Missing {', '.join(a['missingDocuments'])} ({a['uploadedCount']}/{a['totalRequired']} uploaded)" for a in flagged]
                reply_text = (
                    f"Found **{len(flagged)} application(s) with missing required documents**:\n\n" +
                    "\n".join(lines) +
                    "\n\n*Action*: Sellers have been requested to upload remaining certificates before review."
                )
            else:
                reply_text = "All active seller applications have uploaded all required documents."

            return {
                'agent': 'admin_assistant',
                'status': 'success',
                'reply': reply_text,
                'missingDocuments': missing_res,
                'toolsExecuted': tools_executed
            }

        # 4. MANUAL REVIEW APPLICATIONS
        if any(w in p_lower for w in ['manual review', 'closer look', 'needs review', 'flagged for review']):
            tools_executed.append('get_manual_review_applications')
            manual_res = tool_lib.get_manual_review_applications(user_role)
            manual_apps = manual_res.get('applications', [])
            if manual_apps:
                lines = [f"• **{a['companyName']}** (`{a['id']}`): Risk {a['riskScore']}/100 ({a['riskCategory']}) — {a['reason']}" for a in manual_apps]
                reply_text = (
                    f"There are **{len(manual_apps)} application(s) requiring manual review**:\n\n" +
                    "\n".join(lines) +
                    "\n\n*Guidance*: Open these in the Seller Onboarding workspace to inspect original document uploads."
                )
            else:
                reply_text = "There are currently no applications flagged for manual review."

            return {
                'agent': 'admin_assistant',
                'status': 'success',
                'reply': reply_text,
                'manualReview': manual_res,
                'toolsExecuted': tools_executed
            }

        # 5. SUMMARIZE ALL PENDING APPLICATIONS
        if any(w in p_lower for w in ['pending', 'waiting for review', 'summarize all', 'all applications']) or ('pending' in p_lower and 'application' in p_lower) or ('summarize' in p_lower and not extracted_app_id):
            tools_executed.append('summarize_pending_applications')
            pending_res = tool_lib.summarize_pending_applications(user_role)
            pending_apps = pending_res.get('applications', [])
            if pending_apps:
                lines = [f"• **{a['companyName']}** (`{a['id']}`): {a['applicantName']} · {a['city']} | Status: `{a['status']}` | Risk: {a['riskScore']}/100 ({a['riskCategory']})" for a in pending_apps[:8]]
                reply_text = (
                    f"📊 **Marketplace Pending Applications Summary**:\n\n"
                    f"There are currently **{pending_res['pendingCount']} seller application(s) awaiting review**:\n\n" +
                    "\n".join(lines) +
                    f"\n\n*Action*: Review each profile in the admin portal to confirm document readability and location."
                )
            else:
                reply_text = "There are currently no pending seller applications awaiting review. All submitted applications have been processed."

            return {
                'agent': 'admin_assistant',
                'status': 'success',
                'reply': reply_text,
                'pendingSummary': pending_res,
                'toolsExecuted': tools_executed
            }

        # 6. SUMMARIZE SPECIFIC APPLICATION
        if extracted_app_id and any(w in p_lower for w in ['summarize', 'summary', 'detail', 'tell me about', 'profile', 'app']):
            tools_executed.append('summarize_application')
            app_summary = tool_lib.summarize_application(extracted_app_id, user_role)
            if not app_summary.get('found'):
                return {
                    'agent': 'admin_assistant',
                    'status': 'not_found',
                    'reply': app_summary.get('error', f"Application '{extracted_app_id}' was not found in the database. Please verify the application ID."),
                    'toolsExecuted': tools_executed
                }

            docs_text = ", ".join([f"{d['type']} ({d['ocrStatus']})" for d in app_summary['documents']]) if app_summary['documents'] else 'None'
            reply_text = (
                f"📄 **Summary for Application {app_summary['id']}**:\n\n"
                f"• **Business Name**: {app_summary['companyName']}\n"
                f"• **Applicant**: {app_summary['applicantName']}\n"
                f"• **Location**: {app_summary['city']}, {app_summary['state']} (Store Pinned: {'Yes' if app_summary['hasLocation'] else 'No'})\n"
                f"• **Current Status**: `{app_summary['status']}`\n"
                f"• **Risk Score**: {app_summary['riskScore']}/100 ({app_summary['riskCategory']} Risk)\n"
                f"• **Planned Products**: {app_summary['productsCount']} item(s)\n"
                f"• **Documents**: {app_summary['documentsCount']} uploaded [{docs_text}]\n"
                f"• **Submitted Date**: {app_summary['submittedAt']}"
            )
            return {
                'agent': 'admin_assistant',
                'status': 'success',
                'reply': reply_text,
                'summary': app_summary,
                'toolsExecuted': tools_executed
            }

        # 7. DEFAULT AUDIT BRIEFING
        tools_executed.append('audit_seller_applications_state')
        audit_res = tool_lib.audit_seller_applications_state(user_role)
        reply_text = (
            f"Admin Marketplace Briefing: Currently monitoring **{audit_res['totalApplications']} total application(s)**. "
            f"State breakdown: {json.dumps(audit_res['stateBreakdown'])}. "
            f"🚨 **{audit_res['highRiskApplicationsCount']} application(s) flagged as High Risk** due to missing tax credentials or discrepancies."
        )
        return {
            'agent': 'admin_assistant',
            'status': 'success',
            'reply': reply_text,
            'audit': audit_res,
            'toolsExecuted': tools_executed
        }


# Global singleton instance for orchestrator and backward compatibility
agent_engine = AgentEngine()
SathiOrchestrator = AgentEngine
