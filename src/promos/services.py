from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from re import sub

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Q
from django.utils.translation import gettext as _

from src.promos.models import PromoCode, PromoRedemption

SESSION_KEY = 'applied_promo_code'
TWO_PLACES = Decimal('0.01')


@dataclass(frozen=True)
class PromoQuote:
    promo: PromoCode | None
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    error: str = ''


def normalize_code(raw: str) -> str:
    return sub(r'\s+', '', (raw or '')).upper()


def calculate_discount(subtotal: Decimal, percent: int) -> Decimal:
    if subtotal <= 0 or percent <= 0:
        return Decimal('0.00')
    amount = (subtotal * Decimal(percent) / Decimal('100')).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    return min(amount, subtotal)


def quote_cart(request, cart) -> PromoQuote:
    subtotal = Decimal(cart.total_price) if cart else Decimal('0.00')
    raw = request.session.get(SESSION_KEY, '')
    code = normalize_code(raw)
    if not code or subtotal <= 0:
        return PromoQuote(None, subtotal, Decimal('0.00'), subtotal)
    try:
        promo = validate_promo(request, code, subtotal)
    except ValidationError as exc:
        request.session.pop(SESSION_KEY, None)
        return PromoQuote(None, subtotal, Decimal('0.00'), subtotal, error=exc.messages[0])
    discount = calculate_discount(subtotal, promo.discount_percent)
    return PromoQuote(promo, subtotal, discount, subtotal - discount)


def apply_promo(request, raw_code: str, cart) -> PromoQuote:
    subtotal = Decimal(cart.total_price) if cart else Decimal('0.00')
    code = normalize_code(raw_code)
    promo = validate_promo(request, code, subtotal)
    request.session[SESSION_KEY] = promo.code
    request.session.modified = True
    discount = calculate_discount(subtotal, promo.discount_percent)
    return PromoQuote(promo, subtotal, discount, subtotal - discount)


def remove_promo(request) -> None:
    request.session.pop(SESSION_KEY, None)
    request.session.modified = True


def validate_promo(request, code: str, subtotal: Decimal) -> PromoCode:
    code = normalize_code(code)
    if not code:
        raise ValidationError(_('Введіть промокод.'))
    promo = PromoCode.objects.filter(code=code).first()
    if promo is None or not promo.is_active:
        raise ValidationError(_('Промокод недійсний.'))
    if not promo.is_within_dates():
        raise ValidationError(_('Термін дії промокоду закінчився.'))
    if promo.min_order_amount and subtotal < promo.min_order_amount:
        raise ValidationError(
            _('Мінімальна сума для цього коду — %(amount)s грн.')
            % {'amount': promo.min_order_amount.quantize(TWO_PLACES)},
        )
    if promo.max_uses is not None and promo.used_count >= promo.max_uses:
        raise ValidationError(_('Промокод вичерпано.'))
    _check_customer_limit(request, promo)
    return promo


def _check_customer_limit(request, promo: PromoCode, phone: str = '') -> None:
    if promo.max_uses_per_customer is None:
        return
    qs = PromoRedemption.objects.filter(promo=promo)
    if request.user.is_authenticated:
        qs = qs.filter(user=request.user)
    else:
        session_key = request.session.session_key or ''
        filters = Q(session_key=session_key) if session_key else Q(pk__in=[])
        if phone:
            filters |= Q(phone=phone)
        qs = qs.filter(filters)
    if qs.count() >= promo.max_uses_per_customer:
        raise ValidationError(_('Ви вже використали цей промокод.'))


@transaction.atomic
def redeem_on_order(request, order, cart_subtotal: Decimal) -> PromoQuote:
    raw = request.session.get(SESSION_KEY, '')
    if not raw:
        return PromoQuote(None, cart_subtotal, Decimal('0.00'), cart_subtotal)

    promo = PromoCode.objects.select_for_update().filter(code=normalize_code(raw)).first()
    if promo is None:
        request.session.pop(SESSION_KEY, None)
        return PromoQuote(None, cart_subtotal, Decimal('0.00'), cart_subtotal)

    try:
        validate_promo(request, promo.code, cart_subtotal)
        _check_customer_limit(request, promo, phone=order.phone)
    except ValidationError:
        request.session.pop(SESSION_KEY, None)
        return PromoQuote(None, cart_subtotal, Decimal('0.00'), cart_subtotal)

    if promo.max_uses is not None and promo.used_count >= promo.max_uses:
        request.session.pop(SESSION_KEY, None)
        return PromoQuote(None, cart_subtotal, Decimal('0.00'), cart_subtotal)

    discount = calculate_discount(cart_subtotal, promo.discount_percent)
    promo.used_count = F('used_count') + 1
    promo.save(update_fields=['used_count', 'updated_at'])

    PromoRedemption.objects.create(
        promo=promo,
        order=order,
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key or '',
        phone=order.phone or '',
    )
    request.session.pop(SESSION_KEY, None)
    return PromoQuote(promo, cart_subtotal, discount, cart_subtotal - discount)


def create_promo_batch(prefix: str, count: int, **fields) -> list[PromoCode]:
    prefix = normalize_code(prefix)
    if not prefix or count < 1:
        raise ValidationError(_('Вкажіть код і кількість.'))
    if count > 200:
        raise ValidationError(_('Максимум 200 кодів за раз.'))

    created = []
    existing = set(PromoCode.objects.filter(code__startswith=prefix).values_list('code', flat=True))
    seq = 1
    while len(created) < count:
        code = prefix if count == 1 else f'{prefix}-{seq:02d}'
        seq += 1
        if count > 1 and code in existing:
            continue
        if PromoCode.objects.filter(code=code).exists():
            existing.add(code)
            continue
        created.append(PromoCode(code=code, **fields))
        existing.add(code)
        if seq > count + 500:
            raise ValidationError(_('Не вдалося згенерувати унікальні коди.'))
    return PromoCode.objects.bulk_create(created)
