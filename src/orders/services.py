"""Створення замовлення з кошика. Ціна завжди перераховується
на бекенді з поточних Product.price — фронтенд ніколи не диктує суму (SEC-02)."""
from django.db import transaction

from src.cart.services import clear_cart, get_cart
from src.orders.models import Order, OrderItem


class EmptyCartError(Exception):
    pass


@transaction.atomic
def create_order_from_cart(request, form):
    cart = get_cart(request)
    if cart is None or cart.total_quantity == 0:
        raise EmptyCartError('Кошик порожній.')

    items = list(cart.items.select_related('product'))
    subtotal = sum((item.line_total for item in items), start=0)

    order = form.save(commit=False)
    order.subtotal = subtotal
    order.session_key = request.session.session_key or ''
    order.save()

    OrderItem.objects.bulk_create([
        OrderItem(
            order=order,
            product=item.product,
            product_name=item.product.name,
            product_sku=item.product.sku,
            unit_price=item.product.price,
            quantity=item.quantity,
        )
        for item in items
    ])

    clear_cart(cart)
    return order
