import re
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from src.products.models import Brand, Category, Gallery, Product, ProductAttribute

_TAG_RE = re.compile(r'<[^>]+>')
_WHITESPACE_RE = re.compile(r'[ \t]+')


def _html_to_text(value: str) -> str:
    """Груба конвертація HTML-опису постачальника у звичайний текст."""
    if not value:
        return ''
    text = re.sub(r'(?is)<(script|style|svg).*?</\1>', '', value)
    text = re.sub(r'(?i)<(p|div|li|br|h[1-6]|ul|ol)[^>]*>', '\n', text)
    text = _TAG_RE.sub('', text)
    text = _WHITESPACE_RE.sub(' ', text)
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return '\n'.join(lines)


def _parse_decimal(value):
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


class Command(BaseCommand):
    help = 'Імпортує товари, категорії та характеристики з YML/Google Shopping фіда постачальника'

    def add_arguments(self, parser):
        parser.add_argument('file', help='Шлях до XML-файлу фіда')
        parser.add_argument(
            '--download-images',
            action='store_true',
            help='Завантажувати зображення товарів за URL (потребує доступу до мережі)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Обмежити кількість імпортованих товарів (0 = без обмеження, для тестового прогону)',
        )

    def handle(self, *args, **options):
        file_path = options['file']
        try:
            with open(file_path, encoding='utf-8') as fh:
                raw_content = fh.read()
        except OSError as exc:
            raise CommandError(f'Не вдалося прочитати файл: {exc}')

        xml_start = raw_content.find('<?xml')
        if xml_start == -1:
            xml_start = raw_content.find('<rss')
        if xml_start == -1:
            raise CommandError('У файлі не знайдено XML-контент (очікується <?xml ...> або <rss ...>)')

        try:
            root = ET.fromstring(raw_content[xml_start:])
        except ET.ParseError as exc:
            raise CommandError(f'Не вдалося розпарсити XML: {exc}')
        shop = root.find('shop')
        if shop is None:
            raise CommandError('У фіді не знайдено елемент <shop>')

        categories_by_external_id = self._import_categories(shop)
        created, updated = self._import_offers(
            shop,
            categories_by_external_id,
            download_images=options['download_images'],
            limit=options['limit'],
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Готово: {created} товарів створено, {updated} оновлено.'
            )
        )

    def _import_categories(self, shop):
        categories_by_external_id = {}
        pending_parents = []
        categories_el = shop.find('categories')
        if categories_el is None:
            return categories_by_external_id

        for category_el in categories_el.findall('category'):
            external_id = category_el.get('id', '').strip()
            parent_external_id = category_el.get('parentId', '').strip()
            name = (category_el.text or '').strip()
            if not name:
                continue

            category = Category.objects.filter(external_id=external_id).first() if external_id else None
            if category is None:
                category = Category.objects.filter(name=name).first()

            if category is None:
                category = Category.objects.create(
                    name=name,
                    description='',
                    external_id=external_id,
                )
            elif not category.external_id and external_id:
                category.external_id = external_id
                category.save(update_fields=['external_id'])

            if external_id:
                categories_by_external_id[external_id] = category

            if parent_external_id:
                pending_parents.append((category, parent_external_id))

        for category, parent_external_id in pending_parents:
            parent = categories_by_external_id.get(parent_external_id)
            if parent and category.parent_id != parent.pk:
                category.parent = parent
                category.save(update_fields=['parent'])

        self.stdout.write(f'Категорій знайдено у фіді: {len(categories_by_external_id)}')
        return categories_by_external_id

    def _get_or_create_brand(self, name):
        name = (name or '').strip()
        if not name:
            return None
        brand, _ = Brand.objects.get_or_create(name=name)
        return brand

    def _import_offers(self, shop, categories_by_external_id, download_images, limit):
        offers_el = shop.find('offers')
        if offers_el is None:
            raise CommandError('У фіді не знайдено елемент <offers>')

        created_count = 0
        updated_count = 0

        for index, offer_el in enumerate(offers_el.findall('offer')):
            if limit and index >= limit:
                break

            external_id = (offer_el.findtext('id') or '').strip()
            offer_code = offer_el.get('id', '').strip()
            name = (offer_el.findtext('name') or '').strip()
            if not external_id or not name:
                continue

            category_ext_id = (offer_el.findtext('categoryId') or '').strip()
            category = categories_by_external_id.get(category_ext_id)
            if category is None:
                category_name = (offer_el.findtext('categoryName') or 'Без категорії').strip()
                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    defaults={'description': '', 'external_id': category_ext_id},
                )

            brand = self._get_or_create_brand(offer_el.findtext('vendorCode'))

            sale_price = _parse_decimal(offer_el.findtext('salePrice')) or Decimal('0')
            base_price = _parse_decimal(offer_el.findtext('priceRUAH'))
            old_price = base_price if base_price and base_price != sale_price else None

            available = offer_el.get('available', 'false').strip().lower() == 'true'
            description = _html_to_text(offer_el.findtext('description') or '')

            product, created = Product.objects.get_or_create(
                external_id=external_id,
                defaults={
                    'name': name,
                    'category': category,
                },
            )

            product.name = name
            product.description = description
            product.price = sale_price
            product.old_price = old_price
            product.in_stock = available
            product.category = category
            product.brand = brand
            product.vendor_code = offer_code or (offer_el.findtext('code') or '').strip()
            product.barcode = (offer_el.findtext('barcode') or '').strip()
            product.source_url = (offer_el.findtext('url') or '').strip()
            product.save()

            self._import_attributes(product, offer_el)
            self._import_pictures(product, offer_el, download_images)

            if created:
                created_count += 1
            else:
                updated_count += 1

        return created_count, updated_count

    def _import_attributes(self, product, offer_el):
        product.attributes.all().delete()
        for order, param_el in enumerate(offer_el.findall('param')):
            attr_name = (param_el.get('name') or '').strip()
            attr_value = (param_el.text or '').strip()
            if not attr_name or not attr_value:
                continue
            ProductAttribute.objects.create(
                product=product,
                name=attr_name,
                value=attr_value,
                order=order,
            )

    def _import_pictures(self, product, offer_el, download_images):
        import requests

        existing_by_url = {
            gallery.source_url: gallery
            for gallery in product.images.exclude(source_url='')
        }

        for picture_url in offer_el.findall('picture'):
            url = (picture_url.text or '').strip()
            if not url:
                continue

            gallery = existing_by_url.get(url)
            if gallery is None:
                gallery = Gallery(source_url=url)
                is_new = True
            else:
                is_new = False

            if download_images and not gallery.image:
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                except requests.RequestException as exc:
                    self.stderr.write(f'Не вдалося завантажити {url}: {exc}')
                else:
                    file_name = url.split('/')[-1].split('?')[0] or 'image.jpg'
                    gallery.image.save(file_name, ContentFile(response.content), save=False)
                    gallery.save()
            elif is_new:
                gallery.save()

            if is_new:
                product.images.add(gallery)
