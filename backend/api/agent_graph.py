"""
Saathi's brain: a small LangGraph agent with retrieval (RAG).

    classify ──► buy ──────────────────────────────► END
        │
        ├──► greet ────────────────────────────────► END
        │
        └──► retrieve ──► answer ──────────────────► END

- classify: decides what the customer wants (search, buy, ask about policy, say hello).
- retrieve: finds the best matching products and policy passages with a free Hugging Face embedding model
  (BAAI/bge-small-en-v1.5, run locally through fastembed). If the model is unavailable it falls back to keyword matching.
- answer: Gemini (free tier) words a reply using ONLY the retrieved facts. If Gemini is unavailable a plain template is used.
- buy: finds the product the customer means ("buy the first one") and asks the chat to open a confirm-order step.

Prices, stock and ratings are always re-read from the database after retrieval, so the reply can never show stale numbers.
"""

import logging
import os
import re
import threading
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from .agents.llm_provider import UnifiedLLMProvider
from .models import Product

log = logging.getLogger(__name__)
_llm = UnifiedLLMProvider()

POLICY = [
    ('delivery', 'Delivery: most orders from nearby stores arrive the same day or within 1 to 2 days. The delivery fee and time are shown at checkout before you pay. Orders above the free-delivery amount ship free.'),
    ('pickup', 'Pickup: you can collect an order from the store yourself. Choose Pay at Store at checkout and pick the store.'),
    ('payment', 'Payment: Cash on Delivery, Pay at Store, or online with Razorpay in test mode. No real money moves in test mode.'),
    ('returns', 'Returns: delivered items can be returned within 7 days. Open your order and choose Return, or ask for a person. Refunds are processed after inspection.'),
    ('cancel', 'Cancelling: an order can be cancelled before it is out for delivery. Stock is put back and any online payment is marked for refund.'),
    ('tracking', 'Tracking: open Orders, then the order, to see each step and a map route from the store to you once the seller has packed it.'),
    ('sellers', 'Sellers: every product is sold by a local store. You can see which store has it in stock near you on the product page.'),
    ('help', 'Help: ask here, send a question from the Contact page, or say talk to a person to open a support ticket with the full chat attached.'),
]

STOP = set('a an the i me my to for of in on and or is are with want need looking find show give get please some any good best can you do does it this that under below within upto budget rs'.split())
NUMBERS = {'first': 0, '1st': 0, 'one': 0, 'second': 1, '2nd': 1, 'two': 1, 'third': 2, '3rd': 2, 'three': 2, 'fourth': 3, '4th': 3}


class State(TypedDict, total=False):
    message: str
    name: str
    memory: str
    last_cards: List[Dict[str, Any]]
    intent: str
    budget: Optional[int]
    products: List[Dict[str, Any]]
    passages: List[str]
    reply: str
    provider: str
    actions: List[str]
    buy_id: str


# ---------------------------------------------------------------- retrieval --

class Index:
    """Embeds products and policy passages once, then answers nearest-neighbour queries."""

    def __init__(self):
        self.lock = threading.Lock()
        self.key = None
        self.docs: List[Dict[str, Any]] = []
        self.vecs = None
        self.model = None
        self.model_failed = os.getenv('AUTOCART_DISABLE_EMBEDDINGS') == '1'

    def _embedder(self):
        if self.model is None and not self.model_failed:
            try:
                from fastembed import TextEmbedding
                self.model = TextEmbedding('BAAI/bge-small-en-v1.5')
            except Exception as e:  # no network, no model: use keywords instead
                log.warning('Embedding model unavailable, using keyword search: %s', e)
                self.model_failed = True
        return self.model

    @staticmethod
    def _product_text(p: Product) -> str:
        specs = ' '.join(f'{k} {v}' for k, v in (p.specifications or {}).items()) if isinstance(p.specifications, dict) else ''
        return f'{p.name}. {p.brand}. {p.category}. {(p.description or "")[:300]} {specs}'[:700]

    def build(self):
        products = list(Product.objects.all())
        key = (len(products), max((p.id for p in products), default=''))
        if key == self.key:
            return
        docs = [{'kind': 'product', 'id': p.id, 'text': self._product_text(p)} for p in products]
        docs += [{'kind': 'policy', 'id': k, 'text': t} for k, t in POLICY]
        vecs = None
        model = self._embedder()
        if model is not None:
            import numpy as np
            vecs = np.array(list(model.embed([d['text'] for d in docs])), dtype='float32')
            vecs /= np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9
        self.docs, self.vecs, self.key = docs, vecs, key

    def search(self, query: str, kind: str, k: int = 12):
        with self.lock:
            self.build()
            docs = [(i, d) for i, d in enumerate(self.docs) if d['kind'] == kind]
            if self.vecs is not None and self._embedder() is not None:
                import numpy as np
                q = np.array(list(self._embedder().query_embed([query]))[0], dtype='float32')
                q /= np.linalg.norm(q) + 1e-9
                scored = [(float(self.vecs[i] @ q), d) for i, d in docs]
            else:
                words = {w for w in re.findall(r'[a-z0-9]+', query.lower()) if w not in STOP and len(w) > 2}
                scored = [(len(words & set(re.findall(r'[a-z0-9]+', d['text'].lower()))) / (len(words) or 1), d) for _, d in docs]
            scored.sort(key=lambda x: -x[0])
            return scored[:k]


INDEX = Index()


def warm_up():
    """Build the index in the background so the first customer does not wait for it."""
    threading.Thread(target=lambda: INDEX.search('warm up', 'policy', 1), daemon=True).start()


# -------------------------------------------------------------------- nodes --

def _budget(text: str) -> Optional[int]:
    m = re.search(r'(?:under|below|within|upto|up to|less than|budget(?: of)?|max)\s*(?:rs\.?|₹)?\s*([\d,]{3,7})', text.lower())
    return int(m.group(1).replace(',', '')) if m else None


def classify(state: State) -> State:
    t = state['message'].lower()
    intent = 'search'
    if re.fullmatch(r"\s*(hi|hello|hey|hii+|namaste|good (morning|afternoon|evening)|thanks?( you)?|thank you|ok(ay)?)\W*", t):
        intent = 'greet'
    elif re.search(r'\b(buy|order|purchase|get)\b.*\b(it|this|that|first|second|third|one|\d)\b|\bbuy (it|this|that|now)\b|\bplace (the |an )?order\b', t) and re.search(r'\b(buy|order|purchase|place)\b', t):
        intent = 'buy'
    elif re.search(r'\b(deliver|delivery|return|refund|cancel|pay|payment|cod|cash on|pickup|pick up|track|policy|how (does|do|long)|warranty|seller|contact)\b', t) and not re.search(r'\b(under|below|₹|rs)\b', t):
        intent = 'faq'
    return {'intent': intent, 'budget': _budget(state['message'])}


def greet(state: State) -> State:
    n = state.get('name')
    return {'reply': f"Hi{' ' + n if n else ''}! Tell me what you are looking for, like \"headphones under 2000\", or ask about delivery and returns.",
            'actions': ['Find a gift under ₹1,500', 'Track my order', 'How does delivery work?'], 'provider': 'rules'}


def _pick_from_last(text: str, cards: List[Dict[str, Any]]):
    prods = [c for c in cards if c.get('type') == 'product']
    if not prods:
        return None
    for word, idx in NUMBERS.items():
        if re.search(rf'\b{word}\b', text) and idx < len(prods):
            return prods[idx]
    if re.search(r'\b(it|this|that|that one|this one)\b', text) or len(prods) == 1:
        return prods[0]
    return None


def buy(state: State) -> State:
    t = state['message'].lower()
    pick = _pick_from_last(t, state.get('last_cards') or [])
    pid = pick['id'] if pick else ''
    if not pid:  # "buy the logitech mouse": find it by name, but only when the customer actually named something
        words = [w for w in re.findall(r'[a-z0-9]+', t) if w not in STOP and w not in NUMBERS and w not in ('buy', 'order', 'purchase', 'place', 'now', 'cart')]
        hits = INDEX.search(' '.join(words), 'product', 1) if words else []
        if hits and hits[0][0] > 0.6:
            pid = hits[0][1]['id']
    p = Product.objects.filter(id=pid).first() if pid else None
    if not p:
        return {'reply': 'Which product should I order? Search for it first, then say "buy the first one".', 'actions': ['Show me mouse under ₹1,500'], 'provider': 'rules'}
    if p.stock <= 0:
        return {'reply': f'{p.name} is out of stock right now. Want similar options?', 'actions': [f'Show alternatives to {p.name[:30]}'], 'provider': 'rules', 'products': [_dict(p)]}
    return {'reply': f'Good choice. Check the order below for {p.name} (₹{p.price:,.0f}) and confirm when ready.', 'buy_id': p.id, 'products': [_dict(p)], 'provider': 'rules', 'actions': []}


def _dict(p: Product) -> Dict[str, Any]:
    return {'id': p.id, 'name': p.name, 'price': p.price, 'originalPrice': p.originalPrice, 'rating': p.rating, 'stock': p.stock, 'images': p.images or [], 'category': p.category, 'brand': p.brand}


def retrieve(state: State) -> State:
    q = state['message']
    passages = [d['text'] for s, d in INDEX.search(q, 'policy', 2) if s > (0.5 if INDEX.vecs is not None else 0.2)]
    if state['intent'] == 'faq':
        return {'passages': passages or [t for _, t in POLICY[:2]], 'products': []}
    hits = INDEX.search(q, 'product', 14)
    ids = [d['id'] for s, d in hits if s > (0.5 if INDEX.vecs is not None else 0.15)]
    by_id = {p.id: p for p in Product.objects.filter(id__in=ids)}
    prods = [by_id[i] for i in ids if i in by_id]
    cap = state.get('budget')
    if cap:
        prods = [p for p in prods if p.price <= cap]
    prods.sort(key=lambda p: (p.stock <= 0, -(p.rating or 0) * min(1, (p.reviewCount or 0) / 50 + 0.5)))
    return {'products': [_dict(p) for p in prods[:4]], 'passages': passages}


SYSTEM = (
    "You are Saathi, the friendly shopping assistant of AutoCart, a marketplace of local Mumbai stores. "
    "Use ONLY the FACTS provided. Never invent products, prices, stock, discounts or policies. "
    "Keep it under 60 words, warm and plain. Do not list every product (cards show them); say which one you would pick and why, using the ratings and price. "
    "If the facts do not answer the question, say so and offer to bring in a person."
)


def answer(state: State) -> State:
    prods, passages, cap, name = state.get('products') or [], state.get('passages') or [], state.get('budget'), state.get('name')
    if state['intent'] == 'faq':
        fallback = passages[0] if passages else 'I could not find that. Want me to bring in a person?'
    elif prods:
        top = prods[0]
        fallback = f"I found {len(prods)} option{'s' if len(prods) > 1 else ''}{f' under ₹{cap:,}' if cap else ''}. I would start with {top['name']} (₹{top['price']:,.0f}, rated {top['rating']:.1f})."
    else:
        fallback = f"I could not find a match{f' under ₹{cap:,}' if cap else ''}. Try a different word or a higher budget, or ask for a person."
    reply, provider = fallback, 'retrieval'
    if _llm.is_configured and (prods or passages):
        facts = '\n'.join([f"PRODUCT: {p['name']} | ₹{p['price']:,.0f} | rating {p['rating']:.1f} | {'in stock' if p['stock'] > 0 else 'OUT OF STOCK'}" for p in prods] + [f'POLICY: {t}' for t in passages])
        try:
            from .langchain_module import get_saathi_lcel_chain
            chain = get_saathi_lcel_chain()
            out_text = chain.invoke({
                'customer_name': name or 'unknown',
                'user_memory': state.get('memory') or 'nothing yet',
                'facts': facts,
                'question': state['message']
            })
            if out_text and out_text.strip():
                reply = out_text.strip()
                provider = 'groq' if _llm.groq.is_configured else 'google-gemini'
        except Exception as e:
            log.warning("LangChain LCEL chain failed, falling back to direct provider: %s", e)
            prompt = f"Customer first name: {name or 'unknown'}\nWhat we know about them: {state.get('memory') or 'nothing yet'}\nFACTS:\n{facts}\nQUESTION: {state['message']}"
            out = _llm.generate(SYSTEM, prompt, 0.4, 300)
            if out.get('text'):
                reply, provider = out['text'].strip(), out['provider']
    actions = []
    if prods:
        actions = ['Buy the first one', 'Show cheaper options', 'Compare these']
    return {'reply': reply, 'provider': provider, 'actions': actions}


def _route(state: State) -> str:
    return {'buy': 'buy', 'greet': 'greet'}.get(state['intent'], 'retrieve')


def _build():
    g = StateGraph(State)
    for name, fn in (('classify', classify), ('greet', greet), ('buy', buy), ('retrieve', retrieve), ('answer', answer)):
        g.add_node(name, fn)
    g.add_edge(START, 'classify')
    g.add_conditional_edges('classify', _route, {'buy': 'buy', 'greet': 'greet', 'retrieve': 'retrieve'})
    g.add_edge('retrieve', 'answer')
    for end in ('greet', 'buy', 'answer'):
        g.add_edge(end, END)
    return g.compile()


GRAPH = _build()


def run(message: str, name: str = '', memory: str = '', last_cards: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Run the agent for one customer message. Returns the same shape the chat endpoint already uses."""
    state = GRAPH.invoke({'message': message, 'name': name, 'memory': memory, 'last_cards': last_cards or []})
    prods = state.get('products') or []
    return {
        'reply': state.get('reply') or '',
        'cards': prods,
        'products': prods,
        'suggestedActions': state.get('actions') or [],
        'llmProvider': state.get('provider') or 'retrieval',
        'buyProductId': state.get('buy_id', ''),
        'intent': state.get('intent', 'search'),
    }
