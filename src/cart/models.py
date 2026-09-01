from django.conf import settings
from django.db import models

from src.products.models import Product


class Cart(models.Model):
    """Кошик прив'язаний до сесії анонімного відвідувача або до користувача."""

    session_key = models.CharField(max_length=40, db_index=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='carts',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Кошик'
        verbose_name_plural = 'Кошики'
        indexes = [
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        return f'Кошик #{self.pk}'

    @property
    def total_price(self):
        return sum((item.line_total for item in self.items.select_related('product')), start=0)

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Позиція кошика'
        verbose_name_plural = 'Позиції кошика'
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product'], name='unique_cart_product'),
        ]

    def __str__(self):
        return f'{self.product.name} × {self.quantity}'

    @property
    def line_total(self):
        return self.product.price * self.quantity
