"""
Predefined, parameterized backend tools for AutoCart agents.
All database access is through strict, safe, typed queries.
Never executes raw SQL or arbitrary generated code.
"""

import re
from typing import Dict, List, Any, Optional
from django.db.models import Q
from ..models import Product, Order, Seller, Coupon, Category


def product_to_dict(product: Product) -> Dict[str, Any]:
    return {
        'id': product.id,
        'name': product.name,
        'brand': product.brand,
        'category': product.category,
        'price': float(product.price),
        'originalPrice': float(product.originalPrice),
        'discount': int(product.discount),
        'rating': float(product.rating),
        'reviewCount': int(product.reviewCount),
        'stock': int(product.stock),
        'stockStatus': product.stockStatus,
        'description': product.description,
        'specifications': product.specifications or {},
        'seller': product.seller,
        'images': product.images or [],
    }


# =====================================================================
# AGENT A: DISCOVERY TOOLS
# =====================================================================

def search_products(
    query: str,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    limit: int = 6
) -> Dict[str, Any]:
    """
    Search AutoCart product database by keyword, category, brand, budget, and minimum rating.
    Prioritizes in-stock products, extracts natural counts (e.g. 'suggest 5'), and applies strict price bounds.
    """
    q_str = (query or '').strip()
    qs = Product.objects.all()

    # Parse natural language count if present (e.g. "suggest five wireless earbuds", "show 3 laptops")
    count_match = re.search(
        r'\b(?:suggest|show|find|recommend|give|display|top)\s*(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b',
        q_str.lower()
    )
    if count_match:
        c_str = count_match.group(1).lower()
        word_to_num = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}
        c_val = int(c_str) if c_str.isdigit() else word_to_num.get(c_str, limit)
        if 1 <= c_val <= 20:
            limit = c_val

    if category and category.lower() != 'all':
        qs = qs.filter(Q(category__iexact=category) | Q(categoryId__iexact=category))

    if brand:
        qs = qs.filter(brand__iexact=brand.strip())

    if min_price is not None and min_price > 0:
        qs = qs.filter(price__gte=float(min_price))

    if max_price is not None and max_price > 0:
        qs = qs.filter(price__lte=float(max_price))

    if min_rating is not None and min_rating > 0:
        qs = qs.filter(rating__gte=float(min_rating))

    # Also parse natural language budget expressions if present in query (e.g. "₹1,000 se ₹1,500", "under ₹3,000", "under 70k")
    range_match = re.search(
        r'(?:between|from)?\s*[₹rs\.]*\s*([0-9,]+(?:\.[0-9]+)?)\s*(k|thousand|lakh)?\s*(?:se|to|and|-)\s*[₹rs\.]*\s*([0-9,]+(?:\.[0-9]+)?)\s*(k|thousand|lakh)?\s*(?:ke beech)?',
        q_str.lower()
    )
    if range_match:
        try:
            min_v = float(range_match.group(1).replace(',', '').strip())
            if range_match.group(2) in ('k', 'thousand'):
                min_v *= 1000
            elif range_match.group(2) == 'lakh':
                min_v *= 100000

            max_v = float(range_match.group(3).replace(',', '').strip())
            if range_match.group(4) in ('k', 'thousand'):
                max_v *= 1000
            elif range_match.group(4) == 'lakh':
                max_v *= 100000

            if min_v > max_v:
                min_v, max_v = max_v, min_v
            qs = qs.filter(price__gte=min_v, price__lte=max_v)
        except (ValueError, TypeError):
            pass
    else:
        budget_match = re.search(
            r'(?:under|below|less than|within|upto|up to|budget(?: of)?)\s*[₹rs\.]*\s*([0-9,]+(?:\.[0-9]+)?)\s*(k|thousand|lakh)?',
            q_str.lower()
        )
        if budget_match and (max_price is None or max_price <= 0):
            try:
                val_str = budget_match.group(1).replace(',', '').strip()
                val = float(val_str)
                unit = budget_match.group(2) or ''
                if unit in ('k', 'thousand'):
                    val *= 1000
                elif unit == 'lakh':
                    val *= 100000
                qs = qs.filter(price__lte=val)
            except (ValueError, TypeError):
                pass

        min_match = re.search(
            r'(?:above|over|more than|greater than|min|minimum)\s*[₹rs\.]*\s*([0-9,]+(?:\.[0-9]+)?)\s*(k|thousand|lakh)?',
            q_str.lower()
        )
        if min_match and (min_price is None or min_price <= 0):
            try:
                val_min = float(min_match.group(1).replace(',', '').strip())
                unit_min = min_match.group(2) or ''
                if unit_min in ('k', 'thousand'):
                    val_min *= 1000
                elif unit_min == 'lakh':
                    val_min *= 100000
                qs = qs.filter(price__gte=val_min)
            except (ValueError, TypeError):
                pass

    # Intelligent Relevance-Ranked Keyword Search
    terms = [t for t in re.findall(r'[a-zA-Z]+', q_str.lower()) if len(t) > 2]
    stop_words = {
        'the', 'and', 'for', 'with', 'under', 'below', 'best', 'good', 'show',
        'find', 'want', 'need', 'please', 'give', 'some', 'what', 'are', 'your',
        'today', 'top', 'rated', 'trending', 'most', 'popular', 'any', 'tell',
        'can', 'you', 'recommend', 'suggest', 'looking', 'suggested', 'five',
        'four', 'three', 'two', 'one', 'six', 'seven', 'eight', 'nine', 'ten'
    }
    search_terms = [t for t in terms if t not in stop_words]

    category_aliases = {
        'electronics': ['Electronics'],
        'gadgets': ['Electronics'],
        'laptop': ['Laptops'],
        'laptops': ['Laptops'],
        'notebook': ['Laptops'],
        'phone': ['Electronics', 'Mobiles', 'Smartphones'],
        'mobile': ['Electronics', 'Mobiles', 'Smartphones'],
        'smartphone': ['Electronics', 'Mobiles', 'Smartphones'],
        'earbuds': ['Electronics', 'Audio'],
        'headphones': ['Electronics', 'Audio'],
        'earphone': ['Electronics', 'Audio'],
        'shoes': ['Fashion', 'Sports & Fitness'],
        'running': ['Fashion', 'Sports & Fitness'],
        'sneakers': ['Fashion', 'Sports & Fitness'],
        'clothing': ['Fashion'],
        'clothes': ['Fashion'],
        'bottle': ['Home & Kitchen', 'Sports & Fitness'],
        'bottles': ['Home & Kitchen', 'Sports & Fitness'],
    }

    def score_product(p):
        name_l = p.name.lower()
        desc_l = (p.description or '').lower()
        brand_l = (p.brand or '').lower()
        cat_l = (p.category or '').lower()

        # Strict exclusion of mismatched accessories:
        # 1. Searching for Laptop: eliminate backpacks, bags, sleeves, stands, skins, coolers, fashion apparel,
        # and non-laptop electronics like mice, keyboards, headphones, earbuds, chargers, cables, monitors, TVs, phones, watches
        if any(w in search_terms for w in ['laptop', 'laptops', 'notebook']):
            disqualifiers = [
                'backpack', 'bag', 'sleeve', 'stand', 'cooler', 'skin', 'case', 'cover',
                'mouse', 'mice', 'keyboard', 'headphone', 'headphones', 'earphone', 'earbuds',
                'cable', 'power bank', 'charger', 'adapter', 'monitor', 'tv', 'watch', 'phone',
                't-shirt', 'shirt', 'jeans', 'pant', 'shoe', 'shoes', 'dress', 'kurta', 'bottle',
                'flask', 'dumbbells', 'treadmill', 'racket', 'book', 'books', 'dal', 'rice', 'oil',
                'mascara', 'wash', 'cream', 'serum', 'air fryer', 'cooktop', 'pillow', 'mattress'
            ]
            if any(re.search(rf'\b{re.escape(acc)}\b', name_l) for acc in disqualifiers) or cat_l in [
                'fashion', 'apparel', 'home & kitchen', 'sports & fitness', 'beauty & personal care',
                'grocery & gourmet', 'books & stationery', 'toys & baby care'
            ]:
                return -9999.0
            laptop_indicators = [
                'laptop', 'notebook', 'macbook', 'ideapad', 'thinkpad', 'vivobook',
                'zenbook', 'pavilion', 'inspiron', 'swift', 'tuf', 'xps', 'legion'
            ]
            if not any(li in name_l for li in laptop_indicators) and cat_l != 'laptops':
                return -9999.0

        # 2. Searching for Earbuds / Headphones: eliminate mice, keyboards, cables, covers, phones, laptops, watches
        if any(w in search_terms for w in ['earbuds', 'earphone', 'headphones', 'tws', 'airpods']):
            if any(re.search(rf'\b{re.escape(acc)}\b', name_l) for acc in ['mouse', 'mice', 'keyboard', 'cable', 'cover', 'strap', 'laptop', 'charger', 'backpack', 'tv', 'monitor', 'smartwatch', 'watch']):
                return -9999.0
            if 'phone' in name_l and 'buds' not in name_l and 'ear' not in name_l:
                return -9999.0
            audio_indicators = ['earbuds', 'earphone', 'headphones', 'tws', 'airpods', 'buds', 'airbass', 'headset', 'anc', 'wireless']
            if not any(ai in name_l for ai in audio_indicators) and cat_l not in ['audio', 'electronics']:
                return -9999.0

        # 3. Searching for Shoes / Footwear: eliminate t-shirts, shirts, jeans, pants, kurtas, bags, bottles
        if any(w in search_terms for w in ['shoes', 'sneakers', 'running', 'footwear']):
            if any(re.search(rf'\b{re.escape(acc)}\b', name_l) for acc in ['t-shirt', 'shirt', 'jeans', 'pant', 'kurta', 'dress', 'backpack', 'bottle', 'watch']):
                return -9999.0

        # 4. Searching for Water Bottles: eliminate backpacks, apparel, cosmetics
        if any(w in search_terms for w in ['bottle', 'bottles', 'flask', 'sipper']):
            if any(re.search(rf'\b{re.escape(acc)}\b', name_l) for acc in ['t-shirt', 'shirt', 'backpack', 'shoes', 'mascara', 'cosmetic']):
                return -9999.0

        # 5. Searching for Mobile / Phone: eliminate headphones, earbuds, cases, cables, laptops, watches
        if any(w in search_terms for w in ['phone', 'mobile', 'smartphone', 'mobiles', 'smartphones']):
            if any(re.search(rf'\b{re.escape(acc)}\b', name_l) for acc in [
                'headphone', 'headphones', 'earphone', 'earphones', 'earbuds', 'tws', 'airpods', 'buds', 'headset',
                'case', 'cover', 'screen protector', 'tempered glass', 'cable', 'charger', 'power bank',
                'laptop', 'mouse', 'keyboard', 'backpack', 'watch', 'smartwatch'
            ]):
                return -9999.0
            phone_indicators = ['phone', 'mobile', 'smartphone', 'galaxy', 'iphone', 'redmi', 'realme', 'oneplus', 'pixel', 'nord', 'poco', 'vivo', 'oppo', 'motorola']
            if not any(pi in name_l for pi in phone_indicators) and cat_l not in ['mobiles', 'smartphones', 'electronics']:
                return -9999.0

        score = float(p.rating or 4.0) * 2.0

        # In-stock items receive significant priority boost
        if p.stock > 0 and p.stockStatus != 'Out of Stock':
            score += 20.0
        else:
            score -= 10.0

        # Reward term occurrences
        for term in search_terms:
            if term in name_l:
                score += 15
            elif term in brand_l:
                score += 10
            elif term in cat_l:
                score += 8
            elif term in desc_l:
                score += 4

        return score

    if search_terms:
        # Build candidate pool from name, brand, category, or description
        name_expr = Q()
        expanded_terms = set(search_terms)
        for t in search_terms:
            if t.endswith('s') and len(t) > 3:
                expanded_terms.add(t[:-1])
            elif not t.endswith('s'):
                expanded_terms.add(t + 's')
        if any(t in ['earbuds', 'earphone', 'headphones', 'tws'] for t in search_terms):
            expanded_terms.update(['buds', 'airbass', 'propods', 'airpods', 'tws'])
        if any(t in ['laptop', 'laptops', 'notebook'] for t in search_terms):
            expanded_terms.update(['laptop', 'vivobook', 'thinkpad', 'macbook', 'ideapad', 'pavilion', 'swift', 'tuf', 'xps', 'inspiron'])

        for term in list(expanded_terms)[:10]:
            name_expr |= Q(name__icontains=term) | Q(brand__icontains=term)

        candidates = list(qs.filter(name_expr)[:limit * 6])

        # If searching for laptops specifically, guarantee dedicated laptop pool
        if any(t in ['laptop', 'laptops', 'notebook'] for t in search_terms):
            laptop_q = (
                Q(name__icontains='laptop') | Q(category__iexact='Laptops') |
                Q(name__icontains='macbook') | Q(name__icontains='ideapad') |
                Q(name__icontains='pavilion') | Q(name__icontains='inspiron') |
                Q(name__icontains='swift') | Q(name__icontains='vivobook') |
                Q(name__icontains='tuf') | Q(name__icontains='xps')
            )
            laptop_candidates = list(qs.filter(laptop_q)[:limit * 4])
            for lc in laptop_candidates:
                if lc not in candidates:
                    candidates.append(lc)

        # If pool is small, check category aliases and explicit category
        if len(candidates) < limit:
            cat_expr = Q()
            if category and category.lower() != 'all':
                cat_expr |= Q(category__iexact=category)
            for term in search_terms:
                if term in category_aliases:
                    for target_c in category_aliases[term]:
                        cat_expr |= Q(category__iexact=target_c)
                if term not in ['laptop', 'laptops', 'notebook']:
                    cat_expr |= Q(category__icontains=term)
            if cat_expr:
                more_cat = list(qs.filter(cat_expr)[:limit * 3])
                for item in more_cat:
                    if item not in candidates:
                        candidates.append(item)

        if not candidates:
            desc_expr = Q()
            for term in list(expanded_terms)[:5]:
                desc_expr |= Q(category__icontains=term) | Q(description__icontains=term)
            candidates = list(qs.filter(desc_expr)[:limit * 3])

        # Rank candidates by relevance score and discard disqualified items
        valid_candidates = [c for c in candidates if score_product(c) > 0]
        valid_candidates.sort(key=score_product, reverse=True)
        results = valid_candidates[:limit]
    else:
        # No keyword terms: order by in-stock status, rating, and reviewCount
        results = sorted(
            list(qs[:limit * 3]),
            key=lambda p: (0 if (p.stock > 0 and p.stockStatus != 'Out of Stock') else 1, -float(p.rating or 0), -int(p.reviewCount or 0))
        )[:limit]

    return {
        'success': True,
        'count': len(results),
        'products': [product_to_dict(p) for p in results]
    }


def get_product_details(product_id: str) -> Dict[str, Any]:
    """
    Get full catalog details, specifications, price, and stock status for a specific product ID.
    """
    pid = (product_id or '').strip()
    p = Product.objects.filter(Q(id=pid) | Q(slug=pid)).first()
    if not p:
        return {'found': False, 'error': f'Product "{product_id}" not found in catalog'}
    return {
        'found': True,
        'product': product_to_dict(p)
    }


def compare_products(product_ids: List[str]) -> Dict[str, Any]:
    """
    Compare multiple products side by side using their IDs from the database.
    Returns specs, prices, ratings, and stock status.
    """
    clean_ids = [str(pid).strip() for pid in product_ids if pid]
    products = list(Product.objects.filter(id__in=clean_ids))
    return {
        'count': len(products),
        'comparison': [product_to_dict(p) for p in products]
    }


def filter_products_by_budget(max_budget: float, category: Optional[str] = None) -> Dict[str, Any]:
    """
    Find top rated products strictly within a budget ceiling (INR), optionally by category.
    """
    qs = Product.objects.filter(price__lte=float(max_budget), stock__gt=0)
    if category and category.lower() != 'all':
        qs = qs.filter(Q(category__iexact=category) | Q(categoryId__iexact=category))
    results = list(qs.order_by('-rating', '-reviewCount')[:6])
    return {
        'budget_ceiling': max_budget,
        'count': len(results),
        'products': [product_to_dict(p) for p in results]
    }


def check_product_availability(product_id: str) -> Dict[str, Any]:
    """
    Check real-time stock levels, stock status, and seller information for a product.
    If out of stock, suggests available in-stock alternatives in the same category.
    """
    p = Product.objects.filter(id=product_id.strip()).first()
    if not p:
        return {'found': False, 'error': 'Product not found'}
    
    is_in_stock = p.stock > 0 and p.stockStatus != 'Out of Stock'
    alternatives = []
    if not is_in_stock:
        alt_qs = Product.objects.filter(category=p.category, stock__gt=0).exclude(id=p.id).order_by('-rating')[:3]
        alternatives = [product_to_dict(alt) for alt in alt_qs]

    return {
        'found': True,
        'id': p.id,
        'name': p.name,
        'stock': p.stock,
        'stockStatus': p.stockStatus,
        'isAvailable': is_in_stock,
        'seller': p.seller,
        'alternatives': alternatives
    }


# =====================================================================
# AGENT B: CUSTOMER ENGAGEMENT TOOLS
# =====================================================================

def get_my_orders(customer_email: str, limit: int = 5) -> Dict[str, Any]:
    """
    Retrieve order history and current status for the verified authenticated customer.
    SECURITY: customer_email is enforced by backend session/JWT.
    """
    if not customer_email:
        return {'error': 'Authentication required. No verified customer email provided.', 'orders': []}
    
    orders = list(Order.objects.filter(customerEmail__iexact=customer_email).order_by('-id')[:limit])
    return {
        'email': customer_email,
        'orders_count': len(orders),
        'orders': [
            {
                'id': o.id,
                'date': o.date,
                'totalAmount': float(o.totalAmount),
                'status': o.status,
                'paymentMethod': o.paymentMethod,
                'paymentStatus': o.paymentStatus,
                'itemsCount': len(o.items or []),
                'items': o.items,
                'shippingAddress': o.shippingAddress,
            }
            for o in orders
        ]
    }


def get_my_order_details(order_id: str, customer_email: str) -> Dict[str, Any]:
    """
    Get detailed timeline, shipping address, and tracking info for an order belonging to the customer.
    SECURITY: Verifies that the order strictly belongs to customer_email.
    """
    if not customer_email:
        return {'error': 'Authentication required.'}
    
    order = Order.objects.filter(id=order_id.strip()).first()
    if not order:
        return {'error': f'Order {order_id} not found.'}
    
    if order.customerEmail.lower() != customer_email.lower():
        # Prevent customer data leakage!
        return {'error': 'Access denied: You are not authorized to view this order.'}

    return {
        'id': order.id,
        'date': order.date,
        'totalAmount': float(order.totalAmount),
        'subtotal': float(order.subtotal),
        'tax': float(order.tax),
        'shippingFee': float(order.shippingFee),
        'discountAmount': float(order.discountAmount),
        'paymentMethod': order.paymentMethod,
        'paymentStatus': order.paymentStatus,
        'status': order.status,
        'shippingAddress': order.shippingAddress,
        'items': order.items,
        'timeline': order.timeline,
    }


def get_cart_summary(cart_items: List[Dict[str, Any]], coupon_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculate cart pricing breakdown, delivery fee, and applicable coupon savings.
    Revalidates product prices and stock against live database records.
    """
    raw_items = list(cart_items or [])
    verified_items = []
    subtotal = 0.0

    for item in raw_items:
        pid = str(item.get('id', '')).strip()
        p = Product.objects.filter(id=pid).first() if pid else None
        qty = max(1, int(item.get('quantity', 1)))
        
        # Use verified price from DB if available, else fallback to item's stated price
        unit_price = float(p.price) if p else float(item.get('price', 0))
        item_total = unit_price * qty
        subtotal += item_total

        verified_items.append({
            'id': pid,
            'name': p.name if p else item.get('name', 'Product'),
            'price': unit_price,
            'originalPrice': float(p.originalPrice) if p else float(item.get('originalPrice', unit_price)),
            'quantity': qty,
            'stock': int(p.stock) if p else int(item.get('stock', 10)),
            'stockStatus': p.stockStatus if p else 'In Stock',
            'inStock': (p.stock >= qty) if p else True,
            'images': p.images if p else item.get('images', []),
            'itemTotal': round(item_total, 2)
        })

    delivery_fee = 0.0 if (subtotal > 499 or subtotal == 0) else 40.0
    discount_amount = 0.0
    applied_coupon = None

    if coupon_code:
        coupon = Coupon.objects.filter(code__iexact=coupon_code.strip(), status='Active').first()
        if coupon and subtotal >= coupon.minOrderAmount:
            if coupon.discountType == 'Percentage':
                discount_amount = min((subtotal * coupon.discountValue) / 100.0, coupon.maxDiscount)
            else:
                discount_amount = min(coupon.discountValue, coupon.maxDiscount)
            applied_coupon = coupon.code

    final_total = max(0.0, subtotal - discount_amount + delivery_fee)
    return {
        'items': verified_items,
        'itemCount': sum(it['quantity'] for it in verified_items),
        'subtotal': round(subtotal, 2),
        'deliveryFee': delivery_fee,
        'discountAmount': round(discount_amount, 2),
        'finalTotal': round(final_total, 2),
        'appliedCoupon': applied_coupon,
        'freeShippingEligible': subtotal > 499
    }


def add_to_cart_tool(
    product_id: str,
    quantity: int = 1,
    cart_items: Optional[List[Dict[str, Any]]] = None,
    user_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validates product in database, verifies live stock and price, and updates the cart.
    Returns structured action data with updated cart items and safe error messages.
    """
    clean_id = (product_id or '').strip()
    product = Product.objects.filter(Q(id=clean_id) | Q(slug=clean_id)).first()
    if not product:
        return {
            'success': False,
            'action': 'ADD_TO_CART',
            'error': f"Product '{product_id}' was not found in our catalog.",
            'cartItems': cart_items or [],
            'cartSummary': get_cart_summary(cart_items or [])
        }

    if product.stock <= 0 or product.stockStatus == 'Out of Stock':
        alt_qs = Product.objects.filter(category=product.category, stock__gt=0).exclude(id=product.id).order_by('-rating')[:3]
        return {
            'success': False,
            'action': 'ADD_TO_CART',
            'errorType': 'OUT_OF_STOCK',
            'productId': product.id,
            'error': f"Sorry, {product.name} is currently out of stock.",
            'cartItems': cart_items or [],
            'cartSummary': get_cart_summary(cart_items or []),
            'alternatives': [product_to_dict(alt) for alt in alt_qs]
        }

    valid_qty = max(1, int(quantity or 1))
    if valid_qty > product.stock:
        return {
            'success': False,
            'action': 'ADD_TO_CART',
            'productId': product.id,
            'error': f"Only {product.stock} unit(s) of {product.name} are available in stock.",
            'cartItems': cart_items or [],
            'cartSummary': get_cart_summary(cart_items or [])
        }

    items = list(cart_items or [])
    found = False
    new_items = []
    for item in items:
        if str(item.get('id')) == str(product.id):
            found = True
            new_qty = int(item.get('quantity', 1)) + valid_qty
            if new_qty > product.stock:
                new_qty = product.stock
            new_items.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'originalPrice': float(product.originalPrice),
                'rating': float(product.rating),
                'stock': int(product.stock),
                'images': product.images or [],
                'quantity': new_qty
            })
        else:
            new_items.append(dict(item))

    if not found:
        new_items.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'originalPrice': float(product.originalPrice),
            'rating': float(product.rating),
            'stock': int(product.stock),
            'images': product.images or [],
            'quantity': valid_qty
        })

    summary = get_cart_summary(new_items)
    return {
        'success': True,
        'action': 'ADD_TO_CART',
        'productId': product.id,
        'product': product_to_dict(product),
        'quantity': valid_qty,
        'unitPrice': float(product.price),
        'itemSubtotal': float(product.price) * valid_qty,
        'cartItems': new_items,
        'cartSummary': summary,
        'message': f"Added {valid_qty}x {product.name} (₹{float(product.price):,.0f}) to cart."
    }


def update_cart_quantity_tool(
    product_id: str,
    quantity: int,
    cart_items: Optional[List[Dict[str, Any]]] = None,
    user_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Updates the quantity of a product in the cart.
    If quantity <= 0, the item is removed.
    Validates against live stock in the database.
    """
    clean_id = (product_id or '').strip()
    product = Product.objects.filter(Q(id=clean_id) | Q(slug=clean_id)).first()
    items = list(cart_items or [])

    target_idx = -1
    for i, it in enumerate(items):
        if str(it.get('id')) == clean_id or (product and str(it.get('id')) == str(product.id)):
            target_idx = i
            break

    if target_idx == -1 and product:
        if quantity > 0:
            return add_to_cart_tool(product.id, quantity=quantity, cart_items=cart_items, user_email=user_email)
        return {
            'success': False,
            'action': 'UPDATE_QUANTITY',
            'error': f"{product.name} is not in your cart.",
            'cartItems': items,
            'cartSummary': get_cart_summary(items)
        }
    elif target_idx == -1:
        return {
            'success': False,
            'action': 'UPDATE_QUANTITY',
            'error': "Product not found in cart.",
            'cartItems': items,
            'cartSummary': get_cart_summary(items)
        }

    prod_name = product.name if product else items[target_idx].get('name', 'Product')
    prod_price = float(product.price) if product else float(items[target_idx].get('price', 0))

    if quantity <= 0:
        new_items = [it for i, it in enumerate(items) if i != target_idx]
        summary = get_cart_summary(new_items)
        return {
            'success': True,
            'action': 'UPDATE_QUANTITY',
            'productId': clean_id,
            'product': product_to_dict(product) if product else None,
            'quantity': 0,
            'cartItems': new_items,
            'cartSummary': summary,
            'message': f"Removed {prod_name} from your cart."
        }

    # Validate stock
    if product and quantity > product.stock:
        return {
            'success': False,
            'action': 'UPDATE_QUANTITY',
            'productId': product.id,
            'error': f"Only {product.stock} units of {prod_name} are available in stock.",
            'cartItems': items,
            'cartSummary': get_cart_summary(items)
        }

    new_items = []
    for i, it in enumerate(items):
        if i == target_idx:
            new_items.append({
                'id': it.get('id'),
                'name': prod_name,
                'price': prod_price,
                'originalPrice': float(product.originalPrice) if product else float(it.get('originalPrice', prod_price)),
                'rating': float(product.rating) if product else float(it.get('rating', 0)),
                'stock': int(product.stock) if product else int(it.get('stock', 10)),
                'images': product.images if product else it.get('images', []),
                'quantity': quantity
            })
        else:
            new_items.append(dict(it))

    summary = get_cart_summary(new_items)
    return {
        'success': True,
        'action': 'UPDATE_QUANTITY',
        'productId': clean_id,
        'product': product_to_dict(product) if product else None,
        'quantity': quantity,
        'unitPrice': prod_price,
        'itemSubtotal': prod_price * quantity,
        'cartItems': new_items,
        'cartSummary': summary,
        'message': f"Updated {prod_name} quantity to {quantity}."
    }


def remove_from_cart_tool(
    product_id: str,
    cart_items: Optional[List[Dict[str, Any]]] = None,
    user_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Removes a product from the cart.
    """
    return update_cart_quantity_tool(product_id=product_id, quantity=0, cart_items=cart_items, user_email=user_email)


def get_shipping_policy() -> Dict[str, Any]:
    """
    Returns actual configured shipping policies and delivery timelines for AutoCart.
    """
    return {
        'standardDeliveryDays': '3 to 5 business days',
        'expressDeliveryDays': '1 to 2 business days (metro areas)',
        'freeShippingThreshold': 'Orders above ₹499 qualify for free standard shipping',
        'standardShippingFee': '₹40 for orders under ₹499',
        'deliveryPartners': ['Blue Dart', 'Delhivery', 'Shadowfax'],
        'tracking': 'Real-time tracking available under customer Orders tab once shipped'
    }


def get_return_policy() -> Dict[str, Any]:
    """
    Returns actual configured return and refund rules for AutoCart.
    """
    return {
        'returnWindowDays': 7,
        'conditions': 'Items must be unused, in original packaging with tags and warranty seals intact.',
        'nonReturnableCategories': ['Perishable groceries', 'Personal hygiene products', 'Opened software'],
        'refundMethod': 'Original payment method within 5-7 business days after pickup inspection',
        'exchangeOption': 'Free size/color replacement available for apparel and footwear'
    }


# =====================================================================
# AGENT C: SELLER ONBOARDING & ADMIN TOOLS
# =====================================================================

def validate_seller_application(application_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates seller submission fields against marketplace business rules and computes a compliance score.
    """
    data = application_data or {}
    required = ['name', 'companyName', 'email', 'phone', 'city', 'businessType', 'productCategories']
    missing = [f for f in required if not str(data.get(f) or '').strip()]
    
    risk_points = 0
    checklist = []

    # Email
    email = str(data.get('email', '')).strip()
    if not email or '@' not in email:
        risk_points += 20
        checklist.append({'item': 'Valid business email', 'complete': False, 'priority': 'High'})
    else:
        checklist.append({'item': 'Valid business email', 'complete': True, 'priority': 'High'})

    # Phone
    phone = str(data.get('phone', '')).strip()
    if not phone or len(phone) < 10:
        risk_points += 15
        checklist.append({'item': 'Contact telephone number', 'complete': False, 'priority': 'High'})
    else:
        checklist.append({'item': 'Contact telephone number', 'complete': True, 'priority': 'High'})

    # GSTIN (optional)
    gstin = str(data.get('gstin', '')).strip()
    if gstin:
        if len(gstin) == 15:
            checklist.append({'item': 'GSTIN tax identifier verification', 'complete': True, 'priority': 'Optional'})
        else:
            risk_points += 15
            checklist.append({'item': 'GSTIN tax identifier format', 'complete': False, 'priority': 'Optional'})
    else:
        checklist.append({'item': 'GSTIN tax identifier (optional)', 'complete': True, 'priority': 'Optional'})

    # Identity / KYC
    id_verified = bool(data.get('identityVerified'))
    if not id_verified:
        risk_points += 15
        checklist.append({'item': 'Government Identity / KYC proof', 'complete': False, 'priority': 'High'})
    else:
        checklist.append({'item': 'Government Identity / KYC proof', 'complete': True, 'priority': 'High'})

    # Bank verification
    bank_verified = bool(data.get('bankVerified'))
    if not bank_verified:
        risk_points += 15
        checklist.append({'item': 'Commercial bank account verification', 'complete': False, 'priority': 'High'})
    else:
        checklist.append({'item': 'Commercial bank account verification', 'complete': True, 'priority': 'High'})

    # Business proof document
    biz_proof = bool(data.get('businessProofUploaded'))
    if not biz_proof:
        risk_points += 10
        checklist.append({'item': 'Business incorporation / trade license proof', 'complete': False, 'priority': 'Medium'})
    else:
        checklist.append({'item': 'Business incorporation / trade license proof', 'complete': True, 'priority': 'Medium'})

    # Categories
    cats = data.get('productCategories') or []
    if not cats:
        risk_points += 10
        checklist.append({'item': 'Declared product category alignment', 'complete': False, 'priority': 'Medium'})
    else:
        checklist.append({'item': 'Declared product category alignment', 'complete': True, 'priority': 'Medium'})

    risk_score = min(100, risk_points)
    status_label = (
        'Ready for review' if not missing and risk_score <= 30
        else ('Needs verification' if risk_score <= 55 else 'High verification required')
    )

    return {
        'isValid': len(missing) == 0 and risk_score <= 40,
        'missingFields': missing,
        'riskScore': risk_score,
        'preliminaryStatus': status_label,
        'checklist': checklist,
        'recommendation': 'Submit for administrator human review once documents are uploaded.'
    }


def get_pending_seller_applications(user_role: str) -> Dict[str, Any]:
    """
    List pending seller applications from the database.
    SECURITY: Only accessible to users with ADMIN or STAFF role.
    """
    if user_role not in ('ADMIN', 'STAFF'):
        return {'error': 'Access denied: Administrator permissions required to review seller applications.'}

    pending_sellers = list(Seller.objects.filter(status='Pending'))
    return {
        'count': len(pending_sellers),
        'pendingSellers': [
            {
                'id': s.id,
                'name': s.name,
                'companyName': s.companyName,
                'email': s.email,
                'phone': s.phone,
                'city': s.city,
                'status': s.status,
                'joinedDate': s.joinedDate,
            }
            for s in pending_sellers
        ]
    }


def get_seller_application_status(seller_id: str) -> Dict[str, Any]:
    """
    Retrieve current verification status for a specific seller by ID.
    """
    s = Seller.objects.filter(id=seller_id.strip()).first()
    if not s:
        return {'error': f'Seller with ID {seller_id} not found.'}
    return {
        'id': s.id,
        'name': s.name,
        'companyName': s.companyName,
        'status': s.status,
        'city': s.city,
        'joinedDate': s.joinedDate,
    }


def summarize_seller_application(application_data: Dict[str, Any], user_role: str) -> Dict[str, Any]:
    """
    Creates an executive structured summary of a seller application for human administrators.
    SECURITY: Enforces administrator authorization.
    """
    if user_role not in ('ADMIN', 'STAFF'):
        return {'error': 'Access denied: Administrator permissions required.'}

    validation = validate_seller_application(application_data)
    name = application_data.get('name', 'N/A')
    company = application_data.get('companyName', 'N/A')
    city = application_data.get('city', 'N/A')
    categories = application_data.get('productCategories', [])

    return {
        'sellerOverview': f"{name} ({company}) - {city}",
        'categoryFocus': categories,
        'riskScore': validation['riskScore'],
        'preliminaryStatus': validation['preliminaryStatus'],
        'missingFields': validation['missingFields'],
        'checklist': validation['checklist'],
        'humanAdminActionRequired': 'Final approval or rejection must be confirmed manually by an authorized marketplace administrator in the Sellers dashboard.'
    }


# =====================================================================
# AGENT C: LOCATION & FULFILLMENT TOOLS
# =====================================================================

def find_nearby_stores_for_product(
    product_id: Optional[str] = None,
    lat: float = 19.0760,
    lng: float = 72.8777,
    radius_km: float = 20.0,
    required_quantity: int = 1,
    pin_code: Optional[str] = None
) -> Dict[str, Any]:
    """
    Finds real nearby physical partner stores holding actual inventory within customer radius.
    """
    from ..location_service import find_nearby_stores_with_inventory
    stores = find_nearby_stores_with_inventory(
        product_id=product_id,
        customer_lat=float(lat),
        customer_lng=float(lng),
        max_radius_km=float(radius_km),
        required_quantity=int(required_quantity),
        pin_code=pin_code
    )
    return {
        'productId': product_id,
        'customerLocation': {'lat': lat, 'lng': lng, 'pinCode': pin_code},
        'searchRadiusKm': radius_km,
        'storesFoundCount': len(stores),
        'stores': stores
    }


def check_store_inventory_availability(store_id: str, product_id: str, quantity: int = 1) -> Dict[str, Any]:
    """
    Queries exact real-time physical store inventory for a product SKU.
    """
    from ..models import StoreInventory
    inv = StoreInventory.objects.filter(store_id=store_id.strip(), product_id=product_id.strip()).first()
    if not inv:
        return {'available': False, 'message': 'Product is not stocked at this location.'}

    is_sufficient = inv.availableQuantity >= int(quantity)
    return {
        'storeId': inv.store.id,
        'storeName': inv.store.name,
        'productId': inv.product.id,
        'productName': inv.product.name,
        'availableQuantity': inv.availableQuantity,
        'reservedQuantity': inv.reservedQuantity,
        'storePrice': inv.storePrice,
        'isSufficientStock': is_sufficient,
        'requestedQuantity': quantity
    }


def calculate_fulfillment_quote(
    product_id: str,
    quantity: int = 1,
    store_id: Optional[str] = None,
    lat: float = 19.0760,
    lng: float = 72.8777
) -> Dict[str, Any]:
    """
    Calculates exact checkout quote: item subtotal, distance delivery charge, tax, total, and delivery ETA.
    """
    from ..fulfillment_service import FulfillmentService
    return FulfillmentService.generate_checkout_quote(
        product_id=product_id,
        quantity=int(quantity),
        store_id=store_id,
        customer_lat=float(lat),
        customer_lng=float(lng)
    )


def reserve_store_stock(
    store_id: str,
    product_id: str,
    quantity: int = 1,
    user_email: str = 'customer@example.com'
) -> Dict[str, Any]:
    """
    Atomically reserves store stock for 15 minutes to guarantee item availability during checkout.
    """
    from ..fulfillment_service import FulfillmentService
    return FulfillmentService.create_stock_reservation(
        store_id=store_id,
        product_id=product_id,
        quantity=int(quantity),
        user_email=user_email
    )


# =====================================================================
# AGENT B: CUSTOMER POST-PURCHASE & SUPPORT TOOLS
# =====================================================================

def get_order_fulfillment_tracking(order_id: str, customer_email: str) -> Dict[str, Any]:
    """
    Retrieves live fulfillment progress, courier dispatch status, and road tracking ETA for an order.
    """
    from ..models import OrderFulfillment, Order
    clean_id = order_id.strip()
    order = Order.objects.filter(id=clean_id).first()
    if not order:
        return {'error': f"Order {clean_id} not found."}

    if customer_email and order.customerEmail.lower() != customer_email.lower():
        return {'error': 'Unauthorized: You can only view tracking records for your own orders.'}

    ful = OrderFulfillment.objects.filter(order=order).first()
    if not ful:
        from ..fulfillment_service import FulfillmentService
        ful = FulfillmentService.initiate_fulfillment(order)

    return {
        'orderId': order.id,
        'trackingNumber': ful.trackingNumber,
        'deliveryPartner': ful.deliveryPartner,
        'currentStatus': ful.currentStatus,
        'distanceKm': ful.distanceKm,
        'estimatedMinutes': ful.estimatedDeliveryMinutes,
        'storeName': ful.store.name if ful.store else 'AutoCart Fulfillment Hub',
        'timeline': ful.timeline
    }


def check_order_return_eligibility(order_id: str, customer_email: str) -> Dict[str, Any]:
    """
    Evaluates backend policy rules to determine if an order is eligible for return/refund.
    """
    from ..models import Order
    order = Order.objects.filter(id=order_id.strip()).first()
    if not order:
        return {'eligible': False, 'reason': f"Order {order_id} not found."}

    if customer_email and order.customerEmail.lower() != customer_email.lower():
        return {'eligible': False, 'reason': 'Unauthorized access.'}

    if order.status not in ('Delivered', 'Confirmed', 'Processing'):
        return {'eligible': False, 'reason': f"Order is currently in '{order.status}' status."}

    return {
        'orderId': order.id,
        'eligible': True,
        'returnWindowDays': 7,
        'orderDate': order.date,
        'refundAmount': float(order.totalAmount),
        'conditions': 'Items must be intact with original packaging, tags, and accessories.',
        'nextStep': 'Initiate return request with reason to receive instant pickup scheduling.'
    }


def request_order_cancellation(order_id: str, reason: str, customer_email: str) -> Dict[str, Any]:
    """
    Cancels an order if it has not yet been shipped, releasing any reserved stock.
    """
    from ..models import Order
    order = Order.objects.filter(id=order_id.strip()).first()
    if not order:
        return {'success': False, 'error': f"Order {order_id} not found."}

    if customer_email and order.customerEmail.lower() != customer_email.lower():
        return {'success': False, 'error': 'Unauthorized.'}

    if order.status in ('Shipped', 'Out for Delivery', 'Delivered'):
        return {
            'success': False,
            'error': f"Order cannot be cancelled directly as it is already {order.status}. You may initiate a free return upon delivery."
        }

    order.status = 'Cancelled'
    order.save()
    return {
        'success': True,
        'orderId': order.id,
        'status': 'Cancelled',
        'refundStatus': 'Initiated to original payment method',
        'cancellationReason': reason
    }


# =====================================================================
# AGENT E: SELLER BUSINESS ASSISTANT TOOLS
# =====================================================================

def generate_seller_product_listing(
    title: str,
    category: str,
    raw_specs: Optional[str] = None,
    seller_name: str = 'Official Partner'
) -> Dict[str, Any]:
    """
    Autonomous listing copilot: drafts SEO-optimized product titles, category tags,
    bullet points, specifications, and suggested competitive price range based on catalog data.
    """
    clean_title = (title or 'Product').strip()
    clean_cat = (category or 'Electronics').strip()

    # Find benchmark products in the same category
    benchmarks = list(Product.objects.filter(category__icontains=clean_cat).order_by('-rating')[:3])
    avg_price = (sum(p.price for p in benchmarks) / len(benchmarks)) if benchmarks else 1999.0

    return {
        'suggestedTitle': f"{clean_title} — Premium Edition",
        'category': clean_cat,
        'recommendedPrice': round(avg_price * 0.95, 2),
        'suggestedMSRP': round(avg_price * 1.3, 2),
        'estimatedDiscount': '25%',
        'draftDescription': (
            f"Experience superior quality and reliable everyday performance with {clean_title}. "
            f"Engineered to meet the highest market standards for {clean_cat.lower()} enthusiasts."
        ),
        'keyFeatures': [
            f"High-durability build designed for everyday {clean_cat.lower()} use",
            "Certified multi-vendor quality check with manufacturer warranty",
            "Fast dispatch ready with AutoCart Hyperlocal store fulfillment"
        ],
        'requiresConfirmation': 'Draft listing prepared. Seller confirmation required before publishing to live marketplace.'
    }


def analyze_seller_inventory_and_pricing(seller_id: str) -> Dict[str, Any]:
    """
    Analyzes live stock health, low inventory warnings, and pricing opportunities for a seller.
    """
    from ..models import StoreInventory, Store
    stores = Store.objects.filter(sellerId=seller_id)
    if not stores.exists():
        stores = Store.objects.filter(seller__icontains='Appario') # Default benchmark demo

    low_stock = []
    healthy_stock = []

    for store in stores:
        invs = StoreInventory.objects.filter(store=store).select_related('product')[:20]
        for inv in invs:
            item_data = {
                'productId': inv.product.id,
                'name': inv.product.name,
                'available': inv.availableQuantity,
                'store': store.name,
                'price': inv.storePrice
            }
            if inv.availableQuantity <= 5:
                low_stock.append(item_data)
            else:
                healthy_stock.append(item_data)

    return {
        'sellerId': seller_id,
        'storesCount': stores.count(),
        'lowStockAlertCount': len(low_stock),
        'lowStockItems': low_stock[:6],
        'healthyStockItemsCount': len(healthy_stock),
        'actionableRecommendations': [
            f"Replenish {len(low_stock)} low-stock items at nearby fulfillment hubs to prevent lost sales.",
            "Enable AutoCart Hyperlocal Same-Day Dispatch for higher ranking.",
            "Review competitive pricing benchmarks for top-moving catalog SKUs."
        ]
    }


# =====================================================================
# AGENT F: ADMIN MARKETPLACE ASSISTANT TOOLS
# =====================================================================

def audit_seller_applications_state(user_role: str) -> Dict[str, Any]:
    """
    Summarizes all pending seller applications across state machine stages for administrator review.
    """
    from ..models import SellerApplication
    if user_role not in ('ADMIN', 'STAFF'):
        return {'error': 'Access denied: Admin permissions required.'}

    apps = list(SellerApplication.objects.all().order_by('-createdAt'))
    state_breakdown = {}
    for a in apps:
        state_breakdown[a.status] = state_breakdown.get(a.status, 0) + 1

    high_risk = [
        {
            'id': a.id,
            'companyName': a.companyName,
            'applicant': a.applicantName,
            'riskScore': a.riskScore,
            'status': a.status,
            'missing': a.missingFields
        }
        for a in apps if a.riskScore >= 50
    ]

    return {
        'totalApplications': len(apps),
        'stateBreakdown': state_breakdown,
        'highRiskApplicationsCount': len(high_risk),
        'highRiskFlagged': high_risk,
        'requiresAdminAction': 'Authorized administrators must execute final decision via the Admin Seller Onboarding workspace.'
    }


def summarize_pending_applications(user_role: str) -> Dict[str, Any]:
    """
    Summarizes all pending seller applications (PENDING_ADMIN_APPROVAL, NEEDS_MANUAL_REVIEW, SUBMITTED).
    """
    from ..models import SellerApplication
    if user_role not in ('ADMIN', 'STAFF'):
        return {'error': 'Access denied: Admin permissions required.', 'success': False}

    pending_statuses = ('PENDING_ADMIN_APPROVAL', 'NEEDS_MANUAL_REVIEW', 'SUBMITTED')
    apps = list(SellerApplication.objects.filter(status__in=pending_statuses).order_by('-riskScore', '-createdAt'))

    summary_list = []
    for a in apps:
        summary_list.append({
            'id': a.id,
            'companyName': a.companyName,
            'applicantName': a.applicantName,
            'city': a.city,
            'status': a.status,
            'riskScore': a.riskScore,
            'riskCategory': a.riskCategory,
            'submittedAt': a.createdAt.strftime('%Y-%m-%d') if a.createdAt else '',
            'documentsCount': a.documents.count(),
            'missingFields': a.missingFields
        })

    return {
        'success': True,
        'pendingCount': len(apps),
        'applications': summary_list
    }


def get_applications_with_missing_docs(user_role: str) -> Dict[str, Any]:
    """
    Finds all seller applications with missing required documents or marked NEEDS_MORE_INFORMATION.
    """
    from ..models import SellerApplication
    from ..seller_docs import REQUIRED_DOC_TYPES
    if user_role not in ('ADMIN', 'STAFF'):
        return {'error': 'Access denied: Admin permissions required.', 'success': False}

    apps = list(SellerApplication.objects.exclude(status__in=('APPROVED', 'REJECTED', 'SUSPENDED')).order_by('-createdAt'))
    flagged = []

    for a in apps:
        uploaded_types = set(a.documents.values_list('docType', flat=True))
        missing = [t for t in REQUIRED_DOC_TYPES if t not in uploaded_types]
        if missing or a.status == 'NEEDS_MORE_INFORMATION':
            flagged.append({
                'id': a.id,
                'companyName': a.companyName,
                'applicantName': a.applicantName,
                'status': a.status,
                'uploadedCount': len(uploaded_types),
                'totalRequired': len(REQUIRED_DOC_TYPES),
                'missingDocuments': missing or a.missingFields,
                'riskScore': a.riskScore
            })

    return {
        'success': True,
        'count': len(flagged),
        'applications': flagged
    }


def explain_application_risk(application_id: str, user_role: str) -> Dict[str, Any]:
    """
    Returns an explainable, deterministic risk breakdown for a specific seller application.
    """
    from ..models import SellerApplication
    from ..risk_service import SellerRiskScoringService
    if user_role not in ('ADMIN', 'STAFF'):
        return {'error': 'Access denied: Admin permissions required.', 'success': False}

    clean_id = (application_id or '').strip()
    app = SellerApplication.objects.filter(id=clean_id).first()
    if not app:
        # Check if caller omitted prefix
        app = SellerApplication.objects.filter(id=f"app-{clean_id}").first()

    if not app:
        return {
            'success': False,
            'found': False,
            'error': f"Application '{application_id}' was not found in the database. Please verify the application ID."
        }

    eval_res = SellerRiskScoringService.evaluate(app)
    return {
        'success': True,
        'found': True,
        'applicationId': app.id,
        'companyName': app.companyName,
        'applicantName': app.applicantName,
        'status': app.status,
        'riskScore': eval_res['riskScore'],
        'riskCategory': eval_res['riskCategory'],
        'scoringVersion': eval_res['scoringVersion'],
        'contributingFactors': eval_res['contributingFactors'],
        'missingInformation': eval_res['missingInformation'],
        'validationDiscrepancies': eval_res['validationDiscrepancies'],
        'verifiedFacts': eval_res['verifiedFacts'],
        'recommendedAction': eval_res['recommendedAction'],
        'explanation': eval_res['explanation']
    }


def get_validation_discrepancies(application_id: Optional[str], user_role: str) -> Dict[str, Any]:
    """
    Retrieves cross-document discrepancies for a specific application or across all pending applications.
    """
    from ..models import SellerApplication
    from ..seller_docs import compare_application
    if user_role not in ('ADMIN', 'STAFF'):
        return {'error': 'Access denied: Admin permissions required.', 'success': False}

    if application_id:
        clean_id = application_id.strip()
        app = SellerApplication.objects.filter(id=clean_id).first() or SellerApplication.objects.filter(id=f"app-{clean_id}").first()
        if not app:
            return {'success': False, 'found': False, 'error': f"Application '{application_id}' was not found."}
        docs = list(app.documents.all())
        cmp = compare_application(app, docs)
        return {
            'success': True,
            'found': True,
            'applicationId': app.id,
            'companyName': app.companyName,
            'discrepancies': [c for c in cmp.get('checks', []) if c.get('status') == 'mismatch'],
            'mismatchCount': cmp.get('mismatches', 0),
            'missingCount': cmp.get('missing', 0)
        }

    # Across all pending applications
    pending = SellerApplication.objects.filter(status__in=('PENDING_ADMIN_APPROVAL', 'NEEDS_MANUAL_REVIEW'))
    results = []
    for a in pending:
        docs = list(a.documents.all())
        cmp = compare_application(a, docs)
        mismatches = [c for c in cmp.get('checks', []) if c.get('status') == 'mismatch']
        if mismatches:
            results.append({
                'id': a.id,
                'companyName': a.companyName,
                'mismatches': mismatches,
                'count': len(mismatches)
            })

    return {
        'success': True,
        'count': len(results),
        'applicationsWithDiscrepancies': results
    }


def get_manual_review_applications(user_role: str) -> Dict[str, Any]:
    """
    Lists applications flagged for manual review with the underlying reasons.
    """
    from ..models import SellerApplication
    if user_role not in ('ADMIN', 'STAFF'):
        return {'error': 'Access denied: Admin permissions required.', 'success': False}

    apps = list(SellerApplication.objects.filter(status='NEEDS_MANUAL_REVIEW').order_by('-riskScore'))
    summary = []
    for a in apps:
        summary.append({
            'id': a.id,
            'companyName': a.companyName,
            'applicantName': a.applicantName,
            'riskScore': a.riskScore,
            'riskCategory': a.riskCategory,
            'reason': a.aiAssessment or 'Unreadable documents or cross-document field discrepancies.'
        })
    return {
        'success': True,
        'count': len(summary),
        'applications': summary
    }


def summarize_application(application_id: str, user_role: str) -> Dict[str, Any]:
    """
    Provides a comprehensive sanitized summary of an application without exposing raw sensitive PII.
    """
    from ..models import SellerApplication
    if user_role not in ('ADMIN', 'STAFF'):
        return {'error': 'Access denied: Admin permissions required.', 'success': False}

    clean_id = (application_id or '').strip()
    app = SellerApplication.objects.filter(id=clean_id).first() or SellerApplication.objects.filter(id=f"app-{clean_id}").first()
    if not app:
        return {'success': False, 'found': False, 'error': f"Application '{application_id}' was not found in the database."}

    docs = list(app.documents.all())
    doc_summary = [{'type': d.docType, 'ocrStatus': d.ocrStatus, 'fileName': d.fileName} for d in docs]

    return {
        'success': True,
        'found': True,
        'id': app.id,
        'companyName': app.companyName,
        'applicantName': app.applicantName,
        'city': app.city,
        'state': app.addressState,
        'status': app.status,
        'riskScore': app.riskScore,
        'riskCategory': app.riskCategory,
        'hasLocation': bool(app.storeLatitude is not None and app.storeLongitude is not None),
        'productsCount': len(app.plannedProducts or []),
        'documentsCount': len(docs),
        'documents': doc_summary,
        'missingFields': app.missingFields,
        'reviewedBy': app.reviewedBy or 'Pending Review',
        'submittedAt': app.createdAt.strftime('%Y-%m-%d') if app.createdAt else ''
    }


class AgentToolLibrary:
    search_products = staticmethod(search_products)
    get_product_details = staticmethod(get_product_details)
    compare_products = staticmethod(compare_products)
    check_product_availability = staticmethod(check_product_availability)
    check_availability = staticmethod(check_product_availability)
    add_to_cart_tool = staticmethod(add_to_cart_tool)
    update_cart_quantity_tool = staticmethod(update_cart_quantity_tool)
    remove_from_cart_tool = staticmethod(remove_from_cart_tool)
    get_cart_summary = staticmethod(get_cart_summary)
    get_cart_summary_tool = staticmethod(get_cart_summary)
    summarize_pending_applications = staticmethod(summarize_pending_applications)
    get_applications_with_missing_docs = staticmethod(get_applications_with_missing_docs)
    explain_application_risk = staticmethod(explain_application_risk)
    get_validation_discrepancies = staticmethod(get_validation_discrepancies)
    get_manual_review_applications = staticmethod(get_manual_review_applications)
    summarize_application = staticmethod(summarize_application)



