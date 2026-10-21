"""Numbers behind the seller dashboard charts, computed only from the seller's own products and the orders containing them."""

import datetime

from django.utils import timezone

from .commission import fee_for, rate_for
from .models import Order


def _day(order):
    try:
        return datetime.date.fromisoformat(str(order.date)[:10])
    except ValueError:
        return None


def analytics(products, days=30):
    by_id = {p.id: p for p in products}
    today = timezone.localdate()
    series = {today - datetime.timedelta(days=i): {'revenue': 0.0, 'units': 0, 'orders': 0} for i in range(days)}
    per_product, per_category = {}, {}
    gross = fees = 0.0
    cost_total, cost_revenue, no_cost = 0.0, 0.0, set()
    for o in Order.objects.exclude(status='Cancelled'):
        mine = [i for i in (o.items or []) if str(i.get('id')) in by_id]
        if not mine:
            continue
        d = _day(o)
        for i in mine:
            p = by_id[str(i.get('id'))]
            q, amount = int(i.get('quantity') or 0), float(i.get('price') or 0) * int(i.get('quantity') or 0)
            gross += amount
            fees += fee_for(p.category, amount)
            if p.costPrice > 0:
                cost_total += p.costPrice * q
                cost_revenue += amount - fee_for(p.category, amount)
            else:
                no_cost.add(p.name)
            e = per_product.setdefault(p.id, {'name': p.name, 'units': 0, 'revenue': 0.0})
            e['units'] += q
            e['revenue'] += amount
            per_category[p.category] = per_category.get(p.category, 0) + amount
            if d in series:
                series[d]['revenue'] += amount
                series[d]['units'] += q
        if d in series:
            series[d]['orders'] += 1
    top = sorted(per_product.values(), key=lambda x: x['revenue'], reverse=True)[:6]
    return {
        'salesByDay': [{'date': d.isoformat(), 'label': d.strftime('%d %b'), **{k: round(v) for k, v in v_.items()}} for d, v_ in sorted(series.items())],
        'topProducts': [{**t, 'revenue': round(t['revenue'])} for t in top],
        'categoryMix': [{'category': c, 'revenue': round(r), 'commissionPercent': rate_for(c)} for c, r in sorted(per_category.items(), key=lambda x: -x[1])],
        'earnings': {'gross': round(gross), 'commission': round(fees), 'youKeep': round(gross - fees)},
        # Profit only counts products where the seller entered a cost price; the rest are listed so they know what is missing.
        'profit': {'amount': round(cost_revenue - cost_total), 'costKnown': round(cost_total) > 0, 'productsWithoutCost': sorted(no_cost)[:8]},
    }
