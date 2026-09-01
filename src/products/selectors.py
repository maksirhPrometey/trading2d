"""Селектори каталогу: увесь query-building живе тут, views.py лишається тонким."""
from decimal import Decimal, InvalidOperation

from django.db.models import Max, Min, Q

from src.products.models import Category, Product

PRODUCTS_PER_PAGE = 8

SORT_OPTIONS = {
    'recommended': ('-is_bestseller', '-created_at'),
    'new': ('-created_at',),
    'popular': ('-is_bestseller', '-stock_quantity'),
    'price_asc': ('price',),
    'price_desc': ('-price',),
}


def parse_decimal(value):
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def normalize_sort(value):
    return value if value in SORT_OPTIONS else 'recommended'


def filter_catalog_products(*, query='', category=None, in_stock_only=False,
                             price_min=None, price_max=None, sort='recommended'):
    products = Product.objects.select_related('category').prefetch_related('images')

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(name_ru__icontains=query)
            | Q(name_en__icontains=query)
            | Q(description__icontains=query)
            | Q(description_ru__icontains=query)
            | Q(description_en__icontains=query)
            | Q(sku__icontains=query)
        )

    if category is not None:
        products = products.filter(category=category)

    if in_stock_only:
        products = products.filter(in_stock=True)

    if price_min is not None:
        products = products.filter(price__gte=price_min)

    if price_max is not None:
        products = products.filter(price__lte=price_max)

    return products.order_by(*SORT_OPTIONS[normalize_sort(sort)])


def get_catalog_categories():
    return Category.objects.select_related('parent').order_by('name')


def get_price_bounds():
    return Product.objects.aggregate(min_price=Min('price'), max_price=Max('price'))


def get_related_products(product, limit=4):
    return (
        Product.objects.filter(category=product.category)
        .exclude(pk=product.pk)
        .prefetch_related('images')[:limit]
    )
