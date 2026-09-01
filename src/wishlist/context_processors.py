from src.wishlist.services import get_wishlist_product_ids


def wishlist(request):
    """Дає доступ до id товарів у обраному в будь-якому шаблоні —
    для бейджа `#wishlist-count` у хедері та активного стану сердечка
    на картках товару (без окремого запиту на кожну картку)."""
    wishlist_ids = get_wishlist_product_ids(request)
    return {
        'wishlist_ids': wishlist_ids,
        'wishlist_count': len(wishlist_ids),
    }
