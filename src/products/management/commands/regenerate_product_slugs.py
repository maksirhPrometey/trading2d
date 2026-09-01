from django.core.management.base import BaseCommand

from src.products.models import Product
from src.products.utils import ukrainian_slugify


class Command(BaseCommand):
    help = 'Перегенерує slug для товарів з українськими назвами'

    def handle(self, *args, **options):
        updated = 0
        for product in Product.objects.all():
            base = ukrainian_slugify(product.name, fallback=f'product-{product.pk}')
            slug = base
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=product.pk).exists():
                slug = f'{base}-{counter}'
                counter += 1
            if product.slug != slug:
                product.slug = slug
                product.save(update_fields=['slug'])
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Оновлено slug: {updated}'))
