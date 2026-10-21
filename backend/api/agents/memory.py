"""
In-memory session and conversation memory manager for AutoCart agents.
Privacy-conscious: Never stores passwords, tokens, or payment credentials.
Sessions are segregated by session ID / authenticated customer identity.
Maintains structured server-side conversation state for multi-turn shopping and reference resolution.
"""

import re
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple


ORDINALS = {
    'first': 0, '1st': 0, 'pehla': 0, 'pehli': 0, '#1': 0, 'number 1': 0, 'no 1': 0, 'option 1': 0, 'item 1': 0, 'product 1': 0,
    'second': 1, '2nd': 1, 'doosra': 1, 'dusra': 1, 'dusri': 1, 'doosri': 1, '#2': 1, 'number 2': 1, 'no 2': 1, 'option 2': 1, 'item 2': 1, 'product 2': 1,
    'third': 2, '3rd': 2, 'teesra': 2, 'teesri': 2, 'tisra': 2, '#3': 2, 'number 3': 2, 'no 3': 2, 'option 3': 2, 'item 3': 2, 'product 3': 2,
    'fourth': 3, '4th': 3, 'chautha': 3, 'choutha': 3, '#4': 3, 'number 4': 3, 'no 4': 3, 'option 4': 3, 'item 4': 3, 'product 4': 3,
    'fifth': 4, '5th': 4, 'panchwa': 4, 'paanchwa': 4, '#5': 4, 'number 5': 4, 'no 5': 4, 'option 5': 4, 'item 5': 4, 'product 5': 4,
    'sixth': 5, '6th': 5, 'chatha': 5, 'chhatwa': 5, 'chhatha': 5, '#6': 5, 'number 6': 5, 'no 6': 5, 'option 6': 5, 'item 6': 5, 'product 6': 5,
    'seventh': 6, '7th': 6, 'saatwa': 6, '#7': 6, 'number 7': 6, 'no 7': 6, 'option 7': 6, 'item 7': 6, 'product 7': 6,
    'eighth': 7, '8th': 7, 'aathwa': 7, '#8': 7, 'number 8': 7, 'no 8': 7, 'option 8': 7, 'item 8': 7, 'product 8': 7,
    'ninth': 8, '9th': 8, 'nauwa': 8, '#9': 8, 'number 9': 8, 'no 9': 8, 'option 9': 8, 'item 9': 8, 'product 9': 8,
    'tenth': 9, '10th': 9, 'daswa': 9, '#10': 9, 'number 10': 9, 'no 10': 9, 'option 10': 9, 'item 10': 9, 'product 10': 9,
}

WORD_NUMBERS = {
    'one': 1, 'ek': 1, 'two': 2, 'do': 2, 'three': 3, 'teen': 3,
    'four': 4, 'chaar': 4, 'char': 4, 'five': 5, 'paanch': 5, 'panch': 5,
    'six': 6, 'chhe': 6, 'seven': 7, 'saat': 7, 'eight': 8, 'aath': 8,
    'nine': 9, 'nau': 9, 'ten': 10, 'das': 10
}


class SessionMemoryManager:
    """
    Manages bounded conversation history and structured shopping state per session/user.
    Automatically trims old history to control context window and prevent memory leaks.
    """
    _sessions: Dict[str, List[Dict[str, Any]]] = {}
    _states: Dict[str, Dict[str, Any]] = {}
    _timestamps: Dict[str, float] = {}
    MAX_MESSAGES_PER_SESSION = 24
    SESSION_TTL_SECONDS = 3600 * 2  # 2 hours

    @classmethod
    def _clean_expired(cls):
        now = time.time()
        expired = [sid for sid, ts in cls._timestamps.items() if now - ts > cls.SESSION_TTL_SECONDS]
        for sid in expired:
            cls._sessions.pop(sid, None)
            cls._states.pop(sid, None)
            cls._timestamps.pop(sid, None)

    @classmethod
    def get_session_key(cls, session_id: Optional[str] = None, customer_email: Optional[str] = None) -> str:
        s_id = (session_id or '').strip()
        c_email = (customer_email or '').strip()

        # Handle swapped arguments gracefully
        if '@' in s_id and not c_email:
            c_email, s_id = s_id, ''
        elif '@' in s_id and '@' not in c_email:
            c_email, s_id = s_id, c_email

        c_email = c_email.lower().strip()
        if c_email and s_id:
            return f"user:{c_email}:{s_id}"
        if c_email:
            return f"user:{c_email}"
        if s_id:
            return f"anon:{s_id}"
        return "anon:default"

    @classmethod
    def get_history(cls, session_key: str) -> List[Dict[str, Any]]:
        cls._clean_expired()
        return list(cls._sessions.get(session_key, []))

    @classmethod
    def get_state(cls, session_key: str) -> Dict[str, Any]:
        cls._clean_expired()
        state = cls._states.get(session_key)
        if state is None:
            if session_key.startswith("user:"):
                state = cls._states.get(session_key[5:])
            else:
                state = cls._states.get(f"user:{session_key}")

        if state is None and session_key.startswith("user:") and session_key.count(":") >= 2:
            base_key = ":".join(session_key.split(":")[:2])
            state = cls._states.get(base_key)
        
        if state is None:
            state = {
                'conversation_id': session_key,
                'user_email': '',
                'recommendation_list_id': '',
                'ordered_product_ids': [],
                'displayed_products': [],
                'recommendations': [],
                'selected_product_id': None,
                'selected_product': None,
                'quantity': 1,
                'pending_action': None,
                'delivery_address': None,
                'pincode_context': None,
                'last_tool_execution': None,
                'last_stores': [],
                'selected_store': None,
                'cart_items': [],
            }
            cls._states[session_key] = state
            cls._timestamps[session_key] = time.time()
        return dict(state)

    @classmethod
    def get_displayed_products(cls, session_key: str) -> List[Dict[str, Any]]:
        return list(cls.get_state(session_key).get('displayed_products', []))

    @classmethod
    def update_state(cls, session_key: str, updates: Dict[str, Any]):
        cls._clean_expired()
        if session_key not in cls._states:
            cls.get_state(session_key)
        cls._states[session_key].update(updates)
        cls._timestamps[session_key] = time.time()

    @classmethod
    def set_recommendations(cls, session_key: str, products: List[Dict[str, Any]], rec_id: Optional[str] = None):
        """
        Stores the authoritative ordered list of products returned to the customer.
        Preserves exact display order and stable database IDs.
        """
        list_id = rec_id or f"rec_{uuid.uuid4().hex[:8]}"
        ordered_ids = [p['id'] for p in products]
        cls.update_state(session_key, {
            'recommendation_list_id': list_id,
            'ordered_product_ids': ordered_ids,
            'displayed_products': products,
            'recommendations': products,
            'last_products': products,
            'selected_product_id': products[0]['id'] if products else None,
            'selected_product': products[0] if products else None,
            'quantity': 1,
            'pending_action': None,
        })

    @classmethod
    def set_selected_product(
        cls,
        session_key: str,
        product: Dict[str, Any],
        quantity: Optional[int] = None,
        pending_action: Optional[str] = None
    ):
        updates: Dict[str, Any] = {
            'selected_product_id': product['id'],
            'selected_product': product,
        }
        if quantity is not None:
            updates['quantity'] = quantity
        if pending_action is not None:
            updates['pending_action'] = pending_action
        cls.update_state(session_key, updates)

    @classmethod
    def set_delivery_address(
        cls,
        session_key: str,
        address: Dict[str, Any],
        pin_code: Optional[str] = None
    ):
        """
        Updates delivery address and PIN code context in conversation state.
        Immediately invalidates stale location-dependent store choices.
        """
        p_code = pin_code or address.get('pinCode') or address.get('pincode')
        updates = {
            'delivery_address': address,
            'pincode_context': p_code,
            'last_stores': [],
            'selected_store': None,
        }
        cls.update_state(session_key, updates)

    @classmethod
    def get_delivery_address(cls, session_key: str) -> Optional[Dict[str, Any]]:
        """Returns the active delivery address from session state, if present."""
        state = cls.get_state(session_key)
        return state.get('delivery_address')

    @classmethod
    def invalidate_location_cache(cls, session_key: str):
        """Invalidates stale location-dependent results after customer address change."""
        cls.update_state(session_key, {
            'last_stores': [],
            'selected_store': None,
        })

    @classmethod
    def extract_quantity(cls, text: str) -> Optional[int]:
        """
        Extracts quantity numbers from English and natural Hinglish requests.
        Examples: 'add two pieces', '2 pieces', 'quantity 3', 'isko do quantity mein add kar',
                  'make it 2', 'update quantity to 4', 'take 2 pieces'.
        """
        t = text.lower().strip()
        # Direct digit match: "add 2 pieces", "quantity: 2", "2 piece", "2 units"
        m = re.search(r'(?:quantity|qty|add|make it|update to|take|le lunga|into)?\s*[:=]?\s*(\d+)\s*(?:pieces?|units?|items?|quantity|qty|kar)?\b', t)
        if m and m.group(1):
            try:
                qty = int(m.group(1))
                if 1 <= qty <= 100:
                    return qty
            except ValueError:
                pass

        # Word number match: "two pieces", "do piece", "teen pieces", "two of that"
        for word, val in WORD_NUMBERS.items():
            pattern = rf'\b(?:add\s+|quantity\s+|qty\s+|make\s+it\s+|update\s+to\s+|take\s+)?{word}\s*(?:pieces?|units?|items?|quantity|qty|kar|piece|wala)?\b'
            if re.search(pattern, t):
                return val

        return None

    @classmethod
    def resolve_product_reference(
        cls,
        session_key: str,
        text: str
    ) -> Tuple[Optional[Dict[str, Any]], str, Optional[str]]:
        """
        Resolves customer references to products from the structured conversation state.
        Supports:
        - Ordinals: 'first', 'second', 'third', 'fourth', 'fifth', 'last', 'pehla', 'dusra', 'teesra', 'aakhri'
        - Superlatives: 'cheapest', 'sasta', 'most expensive', 'mehnga', 'best rated'
        - Demonstratives / Pronouns: 'this', 'that', 'this one', 'isko', 'usko'
        - Earlier suggestion: 'the one you suggested earlier', 'top pick'
        
        Returns:
            (product_dict_or_None, resolution_type, clarification_or_error_message)
        """
        state = cls.get_state(session_key)
        displayed = state.get('displayed_products') or []
        t = text.lower().strip()

        # Check for empty recommendations state
        if not displayed:
            # Check if there is an active selected product
            if state.get('selected_product'):
                return state['selected_product'], 'selected_cached', None
            return None, 'no_state', (
                "I don't have any recent product recommendations saved in this conversation yet. "
                "What kind of product are you looking for?"
            )

        # 1. Superlatives (cheapest / lowest price / sasta)
        if any(w in t for w in ['cheapest', 'cheaper', 'sasta', 'sabse sasta', 'lowest price', 'kam price', 'least expensive']):
            sorted_by_price = sorted(displayed, key=lambda x: float(x.get('price', 0)))
            return sorted_by_price[0], 'cheapest', None

        # 2. Superlatives (most expensive / mehnga / highest price)
        if any(w in t for w in ['most expensive', 'expensive', 'mehnga', 'sabse mehnga', 'highest price', 'costliest']):
            sorted_by_price = sorted(displayed, key=lambda x: float(x.get('price', 0)), reverse=True)
            return sorted_by_price[0], 'most_expensive', None

        # 3. Superlatives (best rated / highest rating)
        if any(w in t for w in ['best rated', 'highest rating', 'top rated', 'highest rated', 'sabse accha']):
            sorted_by_rating = sorted(displayed, key=lambda x: float(x.get('rating', 0)), reverse=True)
            return sorted_by_rating[0], 'best_rated', None

        # 4. Ordinal: 'last' / 'aakhri'
        if any(w in t for w in ['last', 'last one', 'last product', 'aakhri', 'akhri', 'aakhri wala', 'final']):
            return displayed[-1], 'ordinal_last', None

        # 5. Ordinal numbers (first, second, third, sixth, etc.)
        # Sort keys by length descending to match compound expressions first (e.g. 'option 10' before 'option 1')
        for word, idx in sorted(ORDINALS.items(), key=lambda kv: len(kv[0]), reverse=True):
            # Check boundary match or compound word
            if re.search(rf'\b{re.escape(word)}\b', t) or f"{word} wala" in t or f"{word} wali" in t or f"{word} one" in t:
                if idx < len(displayed):
                    return displayed[idx], f'ordinal_{idx + 1}', None
                else:
                    return None, 'out_of_bounds', (
                        f"I only recommended {len(displayed)} products above. "
                        f"Which of those {len(displayed)} would you prefer?"
                    )

        # 5b. Regex for any numeric ordinal like "6th", "6th one", "option 6", "the 6th product", "#6"
        num_ord = re.search(r'\b(?:the\s+)?(\d+)(?:st|nd|rd|th)\s*(?:one|product|item|option|wala|wali)?\b', t)
        if not num_ord:
            num_ord = re.search(r'\b(?:option|item|product|#|number|no\.?)\s*(\d+)\b', t)
        if num_ord:
            parsed_idx = int(num_ord.group(1)) - 1
            if 0 <= parsed_idx < len(displayed):
                return displayed[parsed_idx], f'ordinal_{parsed_idx + 1}', None
            else:
                return None, 'out_of_bounds', (
                    f"I only recommended {len(displayed)} products above. "
                    f"Which of those {len(displayed)} would you prefer?"
                )

        # 6. Earlier suggestion / top pick
        if any(w in t for w in ['suggested earlier', 'recommended earlier', 'top pick', 'top recommendation', 'earlier one']):
            return displayed[0], 'top_pick', None

        # 7. Demonstrative pronouns ('this', 'that', 'this one', 'that one', 'it', 'isko', 'usko', 'ye', 'yeh', 'woh')
        if any(w in t for w in ['this one', 'that one', 'isko', 'usko', 'same product', 'selected product', 'this', 'that', 'it']):
            if state.get('selected_product'):
                return state['selected_product'], 'selected_active', None
            elif len(displayed) == 1:
                return displayed[0], 'single_match', None
            elif len(displayed) > 1:
                return None, 'ambiguous', (
                    f"Which of the {len(displayed)} recommended products did you mean? "
                    "For example, you can say 'the first one' or 'the second one'."
                )

        # 8. Name/brand matching against displayed products
        for p in displayed:
            name_parts = [w for w in p['name'].lower().split() if len(w) > 3]
            brand_name = (p.get('brand') or '').lower()
            if brand_name and brand_name in t:
                return p, 'brand_match', None
            for part in name_parts:
                if part in t:
                    return p, 'name_match', None

        # 9. Default to active selected product if present
        if state.get('selected_product'):
            return state['selected_product'], 'fallback_selected', None

        # 10. Default to first product if query has buy/cart intent and list is not empty
        if len(displayed) == 1:
            return displayed[0], 'single_default', None

        return None, 'unresolved', None

    @classmethod
    def resolve_comparison_products(cls, session_key: str, text: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Resolves products mentioned for comparison (e.g., 'compare the first and third products',
        'pehla aur teesra compare kar').
        """
        state = cls.get_state(session_key)
        displayed = state.get('displayed_products') or []
        t = text.lower()

        if not displayed:
            return [], "No recently recommended products found to compare. Please search for products first."

        indices = []
        for word, idx in ORDINALS.items():
            if re.search(rf'\b{re.escape(word)}\b', t) and idx not in indices:
                indices.append(idx)

        # Also check 'last'
        if any(w in t for w in ['last', 'aakhri']):
            last_idx = len(displayed) - 1
            if last_idx not in indices:
                indices.append(last_idx)

        valid_products = [displayed[i] for i in indices if i < len(displayed)]
        if len(valid_products) >= 2:
            return valid_products, None

        # If user just said 'compare these' or 'compare products', take top 2 or 3 displayed
        if len(displayed) >= 2:
            return displayed[:3], None

        return displayed, None

    @classmethod
    def add_turn(
        cls,
        session_key: str,
        user_text: str,
        agent_reply: str,
        agent_name: str,
        tools_executed: Optional[List[str]] = None
    ):
        cls._clean_expired()
        if session_key not in cls._sessions:
            cls._sessions[session_key] = []
        
        cls._sessions[session_key].append({
            'role': 'user',
            'content': user_text,
            'timestamp': time.time(),
        })
        cls._sessions[session_key].append({
            'role': 'assistant',
            'agent': agent_name,
            'content': agent_reply,
            'tools_executed': tools_executed or [],
            'timestamp': time.time(),
        })
        
        cls._timestamps[session_key] = time.time()

        if len(cls._sessions[session_key]) > cls.MAX_MESSAGES_PER_SESSION:
            cls._sessions[session_key] = cls._sessions[session_key][-cls.MAX_MESSAGES_PER_SESSION:]

    @classmethod
    def clear_session(cls, session_key: str):
        cls._sessions.pop(session_key, None)
        cls._states.pop(session_key, None)
        cls._timestamps.pop(session_key, None)
