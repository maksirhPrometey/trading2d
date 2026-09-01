from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from src.products.models import Category, Product


class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Product.objects.filter(in_stock=True).only('slug', 'created_at')

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('product_detail', args=[obj.slug])


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return f"{reverse('catalog')}?category={obj.pk}"


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return ['home', 'catalog', 'about_us', 'delivery', 'contact', 'privacy_policy', 'terms_and_conditions']

    def location(self, name):
        return reverse(name)
