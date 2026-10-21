"""
Stock changes in one place: every change is logged, and a seller's auto-restock rule is applied here.

Auto-restock is the seller's own instruction ("when I am down to N, my supplier brings M"). AutoCart adds those units to the shelf
count for them and logs it as an auto-restock, so it is never mistaken for a sale or a manual edit.
"""

from .models import Product, StockLog

LOW = 10


def label(stock):
    return 'Out of Stock' if stock <= 0 else ('Low Stock' if stock <= LOW else 'In Stock')


def set_stock(product, new_stock, reason, by=''):
    """Change a product's stock and write a log row. Returns the change."""
    delta = int(new_stock) - product.stock
    product.stock = int(new_stock)
    product.stockStatus = label(product.stock)
    product.save(update_fields=['stock', 'stockStatus'])
    if delta:
        StockLog.objects.create(productId=product.id, change=delta, stockAfter=product.stock, reason=reason, by=by)
    return delta


def apply_auto_restock(product):
    """After a sale: if the seller's rule is on and stock has fallen to the reorder level, add their usual top-up."""
    if product.autoRestock and product.restockQty > 0 and product.stock <= product.reorderLevel:
        set_stock(product, product.stock + product.restockQty, 'auto-restock', by='auto-restock rule')
        return True
    return False


def log_sale(product, qty):
    StockLog.objects.create(productId=product.id, change=-qty, stockAfter=product.stock, reason='sale')
    apply_auto_restock(product)


def history(product_id, limit=15):
    return [{'change': r.change, 'stockAfter': r.stockAfter, 'reason': r.reason, 'by': r.by, 'at': r.createdAt.isoformat()} for r in StockLog.objects.filter(productId=product_id).order_by('-createdAt', '-id')[:limit]]
