from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from config.views import healthz, robots_txt
from src.products.sitemaps import CategorySitemap, ProductSitemap, StaticViewSitemap
from src.website.i18n_views import set_language

sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('healthz/', healthz, name='healthz'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path(settings.ADMIN_URL, admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('i18n/setlang/', set_language, name='set_language'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

urlpatterns += i18n_patterns(
    path('', include('src.website.urls')),
    path('', include('src.products.urls')),
    path('', include('src.accounts.urls')),
    path('cart/', include('src.cart.urls')),
    path('wishlist/', include('src.wishlist.urls')),
    path('', include('src.orders.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
