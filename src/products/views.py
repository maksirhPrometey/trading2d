from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from src.products import selectors
from src.products.catalog_categories import build_catalog_navigation, resolve_active_nav_group


def _catalog_query_string(request, exclude=('page',)):
    params = request.GET.copy()
    for key in exclude:
        params.pop(key, None)
    return params.urlencode()


def catalog_list(request):
    categories = selectors.get_catalog_categories()

    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    in_stock_only = request.GET.get('in_stock') == '1'
    price_min = selectors.parse_decimal(request.GET.get('price_min', '').strip())
    price_max = selectors.parse_decimal(request.GET.get('price_max', '').strip())
    sort = selectors.normalize_sort(request.GET.get('sort', 'recommended'))

    active_category = None
    if category_id.isdigit():
        active_category = categories.filter(pk=int(category_id)).first()

    products = selectors.filter_catalog_products(
        query=query,
        category=active_category,
        in_stock_only=in_stock_only,
        price_min=price_min,
        price_max=price_max,
        sort=sort,
    )

    paginator = Paginator(products, selectors.PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    page_range = paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1)

    category_nav_groups, category_nav_mode = build_catalog_navigation(categories)
    active_nav_panel = resolve_active_nav_group(category_nav_groups, active_category)

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': categories,
        'category_nav_groups': category_nav_groups,
        'category_nav_mode': category_nav_mode,
        'active_nav_panel': active_nav_panel,
        'active_category': active_category,
        'query': query,
        'sort': sort,
        'in_stock_only': in_stock_only,
        'price_min': request.GET.get('price_min', '').strip(),
        'price_max': request.GET.get('price_max', '').strip(),
        'total_count': paginator.count,
        'query_string': _catalog_query_string(request),
        'price_bounds': selectors.get_price_bounds(),
        'page_range': page_range,
    }
    return render(request, 'products/catalog.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        selectors.Product.objects.select_related('category').prefetch_related('images', 'attributes'),
        slug=slug,
    )
    return render(
        request,
        'products/detail.html',
        {
            'product': product,
            'related_products': selectors.get_related_products(product),
        },
    )
