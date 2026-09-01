from decimal import Decimal
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

from src.products.models import Category, Gallery, Product


DEMO_PRODUCTS = [
    {
        'name': 'Класична сумка "Атлас"',
        'description': 'Шкіряна сумка преміум-класу з мінімалістичним дизайном.',
        'price': Decimal('1920.00'),
        'old_price': Decimal('2400.00'),
        'in_stock': True,
        'stock_quantity': 7,
        'is_bestseller': True,
        'is_new': False,
    },
    {
        'name': 'Годинник "Меридіан"',
        'description': 'Класичний наручний годинник зі сталевим корпусом.',
        'price': Decimal('3450.00'),
        'old_price': None,
        'in_stock': True,
        'stock_quantity': 12,
        'is_bestseller': True,
        'is_new': False,
    },
    {
        'name': 'Портмоне "Флоренція"',
        'description': 'Компактне портмоне з натуральної шкіри.',
        'price': Decimal('935.00'),
        'old_price': Decimal('1100.00'),
        'in_stock': False,
        'stock_quantity': 0,
        'is_bestseller': True,
        'is_new': False,
    },
    {
        'name': 'Ремінь "Кастор"',
        'description': 'Шкіряний ремінь з металевою пряжкою.',
        'price': Decimal('780.00'),
        'old_price': None,
        'in_stock': True,
        'stock_quantity': 15,
        'is_bestseller': True,
        'is_new': False,
    },
    {
        'name': 'Шарф "Норд"',
        'description': 'М\'який шерстяний шарф для холодної погоди.',
        'price': Decimal('1250.00'),
        'old_price': None,
        'in_stock': True,
        'stock_quantity': 9,
        'is_bestseller': False,
        'is_new': True,
    },
    {
        'name': 'Рукавички "Оксфорд"',
        'description': 'Зимові рукавички з підкладкою.',
        'price': Decimal('690.00'),
        'old_price': None,
        'in_stock': True,
        'stock_quantity': 20,
        'is_bestseller': False,
        'is_new': True,
    },
    {
        'name': 'Краватка "Вінтаж"',
        'description': 'Шовкова краватка з класичним візерунком.',
        'price': Decimal('540.00'),
        'old_price': None,
        'in_stock': True,
        'stock_quantity': 18,
        'is_bestseller': False,
        'is_new': True,
    },
    {
        'name': 'Портфель "Абрис"',
        'description': 'Діловий портфель для документів і ноутбука.',
        'price': Decimal('4200.00'),
        'old_price': None,
        'in_stock': True,
        'stock_quantity': 4,
        'is_bestseller': False,
        'is_new': True,
    },
]


def make_placeholder_image(label: str, index: int) -> ContentFile:
    size = 600
    bg = 228 + (index % 4) * 6
    image = Image.new('RGB', (size, size), color=(bg, bg, bg))
    draw = ImageDraw.Draw(image)
    draw.rectangle((24, 24, size - 24, size - 24), outline=(180, 180, 180), width=2)
    text = label[:18]
    draw.text((size // 2, size // 2), text, fill=(120, 120, 120), anchor='mm')
    buffer = BytesIO()
    image.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)
    return ContentFile(buffer.read(), name=f'demo-product-{index + 1}.jpg')


class Command(BaseCommand):
    help = 'Створює 8 тестових товарів для блоків «Хіти продажу» та «Новинки»'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Видалити існуючі тестові товари перед створенням',
        )

    def handle(self, *args, **options):
        if options['reset']:
            deleted, _ = Product.objects.filter(
                name__in=[item['name'] for item in DEMO_PRODUCTS]
            ).delete()
            self.stdout.write(f'Видалено товарів: {deleted}')

        category, _ = Category.objects.get_or_create(
            name='Аксесуари',
            defaults={'description': 'Преміальні аксесуари TRADING 2D'},
        )

        created_count = 0
        for index, item in enumerate(DEMO_PRODUCTS):
            product, created = Product.objects.get_or_create(
                name=item['name'],
                defaults={
                    **item,
                    'category': category,
                },
            )
            if not created:
                for field, value in item.items():
                    setattr(product, field, value)
                product.category = category
                product.save()

            if not product.images.exists():
                gallery = Gallery()
                gallery.image.save(
                    f'demo-product-{index + 1}.jpg',
                    make_placeholder_image(item['name'], index),
                    save=True,
                )
                product.images.add(gallery)

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Готово: {Product.objects.count()} товарів у БД '
                f'({created_count} нових, {Product.objects.filter(is_bestseller=True).count()} хітів, '
                f'{Product.objects.filter(is_new=True).count()} новинок)'
            )
        )
