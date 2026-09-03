from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class PromoCode(models.Model):
    code = models.CharField(max_length=32, unique=True, verbose_name=_('Код'))
    discount_percent = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name=_('Знижка, %'),
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Активний'))
    valid_from = models.DateTimeField(null=True, blank=True, verbose_name=_('Діє з'))
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name=_('Діє до'))
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_('Мін. сума кошика'),
    )
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Ліміт використань'),
        help_text=_('Порожньо — без загального ліміту.'),
    )
    max_uses_per_customer = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Ліміт на покупця'),
        help_text=_('Порожньо — без ліміту на акаунт / сесію.'),
    )
    used_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_('Використано'))
    note = models.CharField(max_length=255, blank=True, verbose_name=_('Нотатка'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Промокод')
        verbose_name_plural = _('Промокоди')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} (−{self.discount_percent}%)'

    def is_within_dates(self, now=None):
        now = now or timezone.now()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return True


class PromoRedemption(models.Model):
    promo = models.ForeignKey(PromoCode, on_delete=models.PROTECT, related_name='redemptions')
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='promo_redemption',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='promo_redemptions',
    )
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    phone = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Використання промокоду')
        verbose_name_plural = _('Використання промокодів')
        constraints = [
            models.UniqueConstraint(fields=['promo', 'order'], name='uniq_promo_order'),
        ]
