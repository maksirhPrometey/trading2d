"""LiqPay-інтеграція: побудова форми оплати й перевірка webhook-підпису.

SEC-07: підпис перевіряється на кожному callback, обробка ідемпотентна
(повторний callback з тим же order_number не подвоює is_paid-статус).
"""
import base64
import hashlib
import json

from django.conf import settings


def build_payment_data(order):
    """Повертає (data, signature) — payload для форми на checkout success."""
    params = {
        'version': '3',
        'public_key': settings.LIQPAY_PUBLIC_KEY,
        'action': 'pay',
        'amount': str(order.subtotal),
        'currency': 'UAH',
        'description': f'Оплата замовлення {order.order_number}',
        'order_id': order.order_number,
        'sandbox': '1' if settings.LIQPAY_SANDBOX else '0',
        'server_url': f'{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/orders/liqpay/callback/',
        'result_url': f'{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/orders/success/{order.order_number}/',
    }
    data = base64.b64encode(json.dumps(params).encode('utf-8')).decode('utf-8')
    signature = _sign(data)
    return data, signature


def verify_callback_signature(data, signature):
    return _sign(data) == signature


def _sign(data):
    raw = settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY
    digest = hashlib.sha1(raw.encode('utf-8')).digest()
    return base64.b64encode(digest).decode('utf-8')


def decode_callback_data(data):
    return json.loads(base64.b64decode(data).decode('utf-8'))
