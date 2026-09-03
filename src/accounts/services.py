"""Злиття гостьових кошика/обраного після логіну або реєстрації."""
from django.db import transaction

from src.cart.models import Cart, CartItem
from src.cart.services import MAX_ITEM_QUANTITY
from src.wishlist.models import Wishlist, WishlistItem


@transaction.atomic
def merge_guest_cart(user, session_key):
    if not session_key or not user.is_authenticated:
        return None

    guest = (
        Cart.objects.filter(session_key=session_key, user=None)
        .prefetch_related('items')
        .first()
    )
    if guest is None:
        return Cart.objects.filter(user=user).first()

    user_cart, _ = Cart.objects.get_or_create(user=user)
    for item in guest.items.all():
        existing = user_cart.items.filter(product_id=item.product_id).first()
        if existing:
            existing.quantity = min(
                existing.quantity + item.quantity,
                MAX_ITEM_QUANTITY,
            )
            existing.save(update_fields=['quantity', 'updated_at'])
        else:
            CartItem.objects.create(
                cart=user_cart,
                product_id=item.product_id,
                quantity=min(item.quantity, MAX_ITEM_QUANTITY),
            )
    guest.delete()
    return user_cart


@transaction.atomic
def merge_guest_wishlist(user, session_key):
    if not session_key or not user.is_authenticated:
        return None

    guest = (
        Wishlist.objects.filter(session_key=session_key, user=None)
        .prefetch_related('items')
        .first()
    )
    if guest is None:
        return Wishlist.objects.filter(user=user).first()

    user_list, _ = Wishlist.objects.get_or_create(user=user)
    for item in guest.items.all():
        WishlistItem.objects.get_or_create(
            wishlist=user_list,
            product_id=item.product_id,
        )
    guest.delete()
    return user_list


def merge_guest_session_data(request):
    """Після успішного login/register — злити session cart/wishlist у user."""
    if not request.user.is_authenticated:
        return
    session_key = request.session.session_key
    if not session_key:
        return
    merge_guest_cart(request.user, session_key)
    merge_guest_wishlist(request.user, session_key)
