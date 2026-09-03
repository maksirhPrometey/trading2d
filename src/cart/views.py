from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from src.cart import services
from src.products.models import Product
from src.promos.services import quote_cart


def cart_detail(request):
    cart = services.get_cart(request)
    if (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        and request.GET.get('fragment') == 'drawer'
    ):
        return render(request, 'components/cart_drawer_panel.html', {'cart': cart})
    return render(request, 'cart/detail.html', {'cart': cart})


@require_POST
def cart_add(request, slug):
    product = get_object_or_404(Product, slug=slug)
    quantity = _parse_quantity(request.POST.get('quantity'), default=1)
    services.add_item(request, product.slug, quantity=quantity)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = services.get_cart(request)
        quote = quote_cart(request, cart)
        return JsonResponse({
            'ok': True,
            'cart_items_count': cart.total_quantity,
            'total_price': str(quote.total),
        })

    messages.success(request, _('«%(name)s» додано в кошик.') % {'name': product.loc('name')})
    return redirect(request.POST.get('next') or reverse('product_detail', args=[slug]))


@require_POST
def cart_update(request, item_id):
    quantity = _parse_quantity(request.POST.get('quantity'), default=1)
    services.update_item_quantity(request, item_id, quantity)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = services.get_cart(request)
        quote = quote_cart(request, cart)
        return JsonResponse({
            'ok': True,
            'cart_items_count': cart.total_quantity if cart else 0,
            'total_price': str(quote.total),
        })
    return redirect('cart_detail')


@require_POST
def cart_remove(request, item_id):
    services.remove_item(request, item_id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = services.get_cart(request)
        return JsonResponse({
            'ok': True,
            'cart_items_count': cart.total_quantity if cart else 0,
        })
    return redirect('cart_detail')


def _parse_quantity(raw_value, default=1):
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return default
    return max(value, 1)
