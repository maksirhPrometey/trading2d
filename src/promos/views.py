from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from src.cart.services import get_cart
from src.promos.forms import ApplyPromoForm
from src.promos.services import apply_promo, remove_promo
from django.core.exceptions import ValidationError


def _next_url(request):
    nxt = request.POST.get('next') or request.META.get('HTTP_REFERER') or ''
    if nxt.startswith('/') and not nxt.startswith('//'):
        return nxt
    return 'cart_detail'


@require_POST
def promo_apply(request):
    cart = get_cart(request)
    form = ApplyPromoForm(request.POST)
    if not cart or cart.total_quantity == 0:
        messages.error(request, _('Додайте товари в кошик, щоб застосувати промокод.'))
        return redirect(_next_url(request))
    if not form.is_valid():
        messages.error(request, _('Введіть промокод.'))
        return redirect(_next_url(request))
    try:
        quote = apply_promo(request, form.cleaned_data['code'], cart)
    except ValidationError as exc:
        messages.error(request, exc.messages[0])
        return redirect(_next_url(request))
    messages.success(
        request,
        _('Промокод %(code)s застосовано: −%(percent)s%%')
        % {'code': quote.promo.code, 'percent': quote.promo.discount_percent},
    )
    return redirect(_next_url(request))


@require_POST
def promo_remove(request):
    remove_promo(request)
    messages.info(request, _('Промокод знято.'))
    return redirect(_next_url(request))
