from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from src.products.models import Product
from src.wishlist import services


def wishlist_detail(request):
    wishlist = services.get_wishlist(request)
    return render(request, 'wishlist/detail.html', {'wishlist': wishlist})


@require_POST
def wishlist_toggle(request, slug):
    get_object_or_404(Product, slug=slug)
    in_wishlist, count = services.toggle_item(request, slug)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'in_wishlist': in_wishlist,
            'count': count,
        })

    return redirect(request.POST.get('next') or 'wishlist_detail')


@require_POST
def wishlist_remove(request, item_id):
    services.remove_item(request, item_id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        wishlist = services.get_wishlist(request)
        return JsonResponse({
            'ok': True,
            'count': wishlist.items.count() if wishlist else 0,
        })
    return redirect('wishlist_detail')
