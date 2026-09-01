from src.cart.services import get_cart


def cart(request):
    """Дає доступ до кошика й кількості товарів у будь-якому шаблоні
    (використовується для бейджа `#cart-count` у хедері)."""
    current_cart = get_cart(request)
    total_quantity = current_cart.total_quantity if current_cart else 0
    return {
        'cart': current_cart,
        'cart_items_count': total_quantity,
    }
