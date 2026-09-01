"""Бізнес-логіка обраного. Views залишаються тонкими й лише викликають ці функції."""
from django.db import transaction

from src.wishlist.models import Wishlist, WishlistItem


def get_or_create_wishlist(request):
    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        return wishlist

    session_key = request.session.session_key
    wishlist, _ = Wishlist.objects.get_or_create(session_key=session_key, user=None)
    return wishlist


def get_wishlist(request):
    """Повертає список обраного без створення нового рядка в БД, якщо його ще немає."""
    if request.user.is_authenticated:
        return Wishlist.objects.filter(user=request.user).prefetch_related(
            'items__product__images'
        ).first()

    session_key = request.session.session_key
    if not session_key:
        return None
    return Wishlist.objects.filter(session_key=session_key).prefetch_related(
        'items__product__images'
    ).first()


def get_wishlist_product_ids(request):
    """Множина id товарів у поточному обраному — для позначення активних
    сердечок на картках товару без додаткового запиту на кожну картку."""
    wishlist = get_wishlist(request)
    if wishlist is None:
        return set()
    return set(wishlist.items.values_list('product_id', flat=True))


@transaction.atomic
def toggle_item(request, product_slug):
    """Додає товар в обране або видаляє, якщо він там вже є.
    Повертає (in_wishlist: bool, total_count: int)."""
    wishlist = get_or_create_wishlist(request)
    item = wishlist.items.select_related('product').filter(product__slug=product_slug).first()
    if item:
        item.delete()
        return False, wishlist.items.count()

    from src.products.models import Product

    product = Product.objects.get(slug=product_slug)
    WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
    return True, wishlist.items.count()


@transaction.atomic
def remove_item(request, item_id):
    wishlist = get_wishlist(request)
    if wishlist is None:
        return
    wishlist.items.filter(pk=item_id).delete()
