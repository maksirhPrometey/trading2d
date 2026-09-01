"""Тонкий клієнт Nova Poshta API (v2.0 JSON) для пошуку міст і відділень
під час чекауту. Використовується через AJAX-ендпоінти
`np_cities` / `np_warehouses` (src/orders/views.py).
"""
import requests
from django.conf import settings

REQUEST_TIMEOUT = 5


class NovaPoshtaError(Exception):
    pass


def _call(model_name, called_method, method_properties=None):
    if not settings.NOVA_POSHTA_API_KEY:
        raise NovaPoshtaError('NOVA_POSHTA_API_KEY не налаштований у .env')

    payload = {
        'apiKey': settings.NOVA_POSHTA_API_KEY,
        'modelName': model_name,
        'calledMethod': called_method,
        'methodProperties': method_properties or {},
    }
    response = requests.post(settings.NOVA_POSHTA_API_URL, json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    if not data.get('success'):
        raise NovaPoshtaError('; '.join(data.get('errors', [])) or 'Nova Poshta API помилка')
    return data.get('data', [])


def search_cities(query, limit=10):
    results = _call('Address', 'searchSettlements', {
        'CityName': query,
        'Limit': str(limit),
    })
    if not results:
        return []
    addresses = results[0].get('Addresses', [])
    return [
        {'ref': item.get('DeliveryCity') or item.get('Ref'), 'name': item.get('Present')}
        for item in addresses
    ]


def get_warehouses(city_ref, limit=50):
    results = _call('AddressGeneral', 'getWarehouses', {
        'CityRef': city_ref,
        'Limit': str(limit),
    })
    return [
        {'ref': item.get('Ref'), 'name': item.get('Description')}
        for item in results
    ]
