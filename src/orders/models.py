from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from src.products.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', _('Нове')
        CONFIRMED = 'confirmed', _('Підтверджено')
        PAID = 'paid', _('Оплачено')
        SHIPPED = 'shipped', _('Відправлено')
        DONE = 'done', _('Завершено')
        CANCELLED = 'cancelled', _('Скасовано')

    class DeliveryMethod(models.TextChoices):
        NOVA_POSHTA_WAREHOUSE = 'np_warehouse', _('Нова Пошта — відділення')
        NOVA_POSHTA_COURIER = 'np_courier', _('Нова Пошта — курʼєр')
        SELF_PICKUP = 'self_pickup', _('Самовивіз')

    class PaymentMethod(models.TextChoices):
        LIQPAY = 'liqpay', _('Оплата картою онлайн (LiqPay)')
        COD = 'cod', _('Оплата при отриманні')

    order_number = models.CharField(max_length=32, unique=True, editable=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NEW)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='orders',
    )

    full_name = models.CharField(max_length=255, verbose_name=_('ПІБ'))
    phone = models.CharField(max_length=32, verbose_name=_('Телефон'))
    email = models.EmailField(blank=True)
    comment = models.TextField(blank=True, verbose_name=_('Коментар до замовлення'))

    delivery_method = models.CharField(max_length=16, choices=DeliveryMethod.choices)
    np_city_name = models.CharField(max_length=255, blank=True, verbose_name=_('Місто (Нова Пошта)'))
    np_city_ref = models.CharField(max_length=64, blank=True)
    np_warehouse_name = models.CharField(max_length=255, blank=True, verbose_name=_('Відділення (Нова Пошта)'))
    np_warehouse_ref = models.CharField(max_length=64, blank=True)

    payment_method = models.CharField(max_length=16, choices=PaymentMethod.choices)
    is_paid = models.BooleanField(default=False)
    payment_transaction_id = models.CharField(max_length=128, blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'Замовлення {self.order_number}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def _generate_order_number(self):
        from django.utils import timezone
        prefix = timezone.now().strftime('%Y%m%d')
        last = Order.objects.filter(order_number__startswith=prefix).order_by('-order_number').first()
        seq = int(last.order_number[-4:]) + 1 if last else 1
        return f'{prefix}-{seq:04d}'


class OrderItem(models.Model):
    """Знімок продукту й ціни на момент замовлення — не залежить від
    подальших змін Product (SEC-02: server-side price snapshot)."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=64, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Позиція замовлення'
        verbose_name_plural = 'Позиції замовлення'

    def __str__(self):
        return f'{self.product_name} × {self.quantity}'

    @property
    def line_total(self):
        return self.unit_price * self.quantity
