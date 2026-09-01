from django.conf import settings
from django.db import models

from src.products.models import Product


class Wishlist(models.Model):
    """Список обраного прив'язаний до сесії анонімного відвідувача або до користувача.
    Дзеркалить структуру src.cart.models.Cart, щоб анонімний список
    зберігався між візитами через session_key так само, як кошик."""

    session_key = models.CharField(max_length=40, db_index=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='wishlists',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Список обраного'
        verbose_name_plural = 'Списки обраного'
        indexes = [
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        return f'Обране #{self.pk}'

    @property
    def total_count(self):
        return self.items.count()


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Позиція обраного'
        verbose_name_plural = 'Позиції обраного'
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(fields=['wishlist', 'product'], name='unique_wishlist_product'),
        ]

    def __str__(self):
        return self.product.name
