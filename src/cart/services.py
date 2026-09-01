"""Бізнес-логіка кошика. Views залишаються тонкими й лише викликають ці функції."""
from django.core.exceptions import ValidationError
from django.db import transaction

from src.cart.models import Cart, CartItem
from src.products.models import Product

MAX_ITEM_QUANTITY = 99


def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    session_key = request.session.session_key
    cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart


def get_cart(request):
    """Повертає кошик без створення нового рядка в БД, якщо його ще немає."""
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user).prefetch_related(
            'items__product__images'
        ).first()

    session_key = request.session.session_key
    if not session_key:
        return None
    return Cart.objects.filter(session_key=session_key).prefetch_related(
        'items__product__images'
    ).first()


@transaction.atomic
def add_item(request, product_slug, quantity=1):
    product = Product.objects.select_for_update().get(slug=product_slug)
    if quantity < 1:
        raise ValidationError('Кількість має бути не менше 1.')

    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': min(quantity, MAX_ITEM_QUANTITY)},
    )
    if not created:
        item.quantity = min(item.quantity + quantity, MAX_ITEM_QUANTITY)
        item.save(update_fields=['quantity', 'updated_at'])
    return item


@transaction.atomic
def update_item_quantity(request, item_id, quantity):
    cart = get_cart(request)
    if cart is None:
        raise CartItem.DoesNotExist
    item = cart.items.select_for_update().get(pk=item_id)
    if quantity <= 0:
        item.delete()
        return None
    item.quantity = min(quantity, MAX_ITEM_QUANTITY)
    item.save(update_fields=['quantity', 'updated_at'])
    return item


@transaction.atomic
def remove_item(request, item_id):
    cart = get_cart(request)
    if cart is None:
        return
    cart.items.filter(pk=item_id).delete()


def clear_cart(cart):
    cart.items.all().delete()
