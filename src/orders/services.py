"""Створення замовлення з кошика. Ціна завжди перераховується
на бекенді з поточних Product.price — фронтенд ніколи не диктує суму (SEC-02)."""
from django.db import transaction

from src.cart.services import clear_cart, get_cart
from src.orders.models import Order, OrderItem
from src.promos.services import redeem_on_order


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
    order.total = subtotal
    order.session_key = request.session.session_key or ''
    if request.user.is_authenticated:
        order.user = request.user
    order.save()
    quote = redeem_on_order(request, order, subtotal)
    if quote.promo:
        order.promo = quote.promo
        order.promo_code = quote.promo.code
        order.discount_percent = quote.promo.discount_percent
        order.discount_amount = quote.discount
        order.total = quote.total
        order.save(update_fields=[
            'promo',
            'promo_code',
            'discount_percent',
            'discount_amount',
            'total',
            'updated_at',
        ])

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
    request.session['last_order_id'] = order.pk
    request.session['last_order_number'] = order.order_number
    return order
