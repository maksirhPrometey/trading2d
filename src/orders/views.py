import json
import logging

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from src.cart.services import get_cart
from src.orders import novaposhta, payment
from src.orders.forms import CheckoutForm
from src.orders.models import Order
from src.orders.services import EmptyCartError, create_order_from_cart

logger = logging.getLogger(__name__)


def checkout(request):
    cart = get_cart(request)
    if cart is None or cart.total_quantity == 0:
        messages.info(request, _('Ваш кошик порожній — додайте товари перед оформленням замовлення.'))
        return redirect('cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                order = create_order_from_cart(request, form)
            except EmptyCartError:
                messages.error(request, _('Кошик порожній.'))
                return redirect('cart_detail')
            return redirect('order_success', order_number=order.order_number)
    else:
        form = CheckoutForm()

    return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    payment_data = payment_signature = None
    if order.payment_method == Order.PaymentMethod.LIQPAY and not order.is_paid:
        payment_data, payment_signature = payment.build_payment_data(order)
    return render(request, 'orders/success.html', {
        'order': order,
        'payment_data': payment_data,
        'payment_signature': payment_signature,
    })


@require_GET
def np_cities(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    try:
        results = novaposhta.search_cities(query)
    except novaposhta.NovaPoshtaError as exc:
        logger.warning('Nova Poshta search_cities failed: %s', exc)
        return JsonResponse({'results': [], 'error': str(exc)}, status=502)
    return JsonResponse({'results': results})


@require_GET
def np_warehouses(request):
    city_ref = request.GET.get('city_ref', '').strip()
    if not city_ref:
        return JsonResponse({'results': []})
    try:
        results = novaposhta.get_warehouses(city_ref)
    except novaposhta.NovaPoshtaError as exc:
        logger.warning('Nova Poshta get_warehouses failed: %s', exc)
        return JsonResponse({'results': [], 'error': str(exc)}, status=502)
    return JsonResponse({'results': results})


@csrf_exempt
@require_POST
def liqpay_callback(request):
    data = request.POST.get('data', '')
    signature = request.POST.get('signature', '')

    if not data or not signature:
        return HttpResponse(status=400)

    if not payment.verify_callback_signature(data, signature):
        logger.warning('LiqPay callback: invalid signature')
        return HttpResponse(status=400)

    payload = payment.decode_callback_data(data)
    order_number = payload.get('order_id')
    status = payload.get('status')
    transaction_id = str(payload.get('payment_id', ''))

    order = Order.objects.filter(order_number=order_number).first()
    if order is None:
        return HttpResponse(status=404)

    # Ідемпотентність: повторний callback з тим самим transaction_id
    # не змінює вже проведений платіж.
    if status in ('success', 'sandbox') and not order.is_paid:
        order.is_paid = True
        order.status = Order.Status.PAID
        order.payment_transaction_id = transaction_id
        order.save(update_fields=['is_paid', 'status', 'payment_transaction_id', 'updated_at'])

    return HttpResponse(status=200)
