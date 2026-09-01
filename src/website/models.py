from django.db import models
from django.utils.translation import gettext_lazy as _

from src.i18n import TranslatableMixin
from src.website.pages import SYSTEM_PAGES_BY_SLUG, page_slug_choices
from src.website.singleton import SingletonModel


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=255)
    site_logo = models.ImageField(upload_to='site_logo/', null=True, blank=True, default='src/core/static/core/img/logo.jpeg')
    site_favicon = models.ImageField(upload_to='site_favicon/', null=True, blank=True)

    class Meta:
        verbose_name = 'Налаштування сайту'
        verbose_name_plural = 'Налаштування сайту'

    def __str__(self):
        return self.site_name


class MainPage(TranslatableMixin, SingletonModel):
    title = models.CharField(max_length=255, default='TRADING 2D')
    title_ru = models.CharField(max_length=255, blank=True, verbose_name='Заголовок (RU)')
    title_en = models.CharField(max_length=255, blank=True, verbose_name='Заголовок (EN)')
    description = models.TextField(blank=True, default='')
    description_ru = models.TextField(blank=True, verbose_name='Опис (RU)')
    description_en = models.TextField(blank=True, verbose_name='Опис (EN)')
    banner_image = models.ImageField(upload_to='main_page/', null=True, blank=True)
    hero_image = models.ForeignKey(
        'products.Gallery',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Фото товару для банера',
        help_text='Пошук — за назвою товару. Якщо не обрано, підбирається автоматично з хітів/новинок.',
    )

    class Meta:
        verbose_name = 'Головна сторінка'
        verbose_name_plural = 'Головна сторінка'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse('home')

    @classmethod
    def singleton_defaults(cls):
        return {
            'title': 'TRADING 2D',
            'description': '',
        }


class HomeShowcaseItem(models.Model):
    class Slot(models.TextChoices):
        BESTSELLER = 'bestseller', _('Хіти продажу')
        NEW_ARRIVAL = 'new_arrival', _('Новинки')

    page = models.ForeignKey(
        MainPage,
        on_delete=models.CASCADE,
        related_name='showcase_items',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        verbose_name='Товар',
    )
    slot = models.CharField(max_length=16, choices=Slot.choices)
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Товар на головній'
        verbose_name_plural = 'Товари на головній'
        ordering = ['slot', 'order', 'pk']
        constraints = [
            models.UniqueConstraint(
                fields=['page', 'product', 'slot'],
                name='unique_home_showcase_product_slot',
            ),
        ]

    def __str__(self):
        return f'{self.get_slot_display()}: {self.product}'


class ContactPage(TranslatableMixin, SingletonModel):
    title = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255, blank=True, verbose_name='Заголовок (RU)')
    title_en = models.CharField(max_length=255, blank=True, verbose_name='Заголовок (EN)')
    description = models.TextField(blank=True, default='')
    description_ru = models.TextField(blank=True, verbose_name='Опис (RU)')
    description_en = models.TextField(blank=True, verbose_name='Опис (EN)')
    image = models.ImageField(upload_to='contact_page/', null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=255)
    address = models.TextField()
    address_ru = models.TextField(blank=True, verbose_name='Адреса (RU)')
    address_en = models.TextField(blank=True, verbose_name='Адреса (EN)')

    class Meta:
        verbose_name = 'Сторінка контактів'
        verbose_name_plural = 'Контакти'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse('contact')

    @classmethod
    def singleton_defaults(cls):
        return {
            'title': 'Контакти',
            'description': (
                '<p>Звертайтеся до нас будь-яким зручним способом — '
                'відповімо протягом робочого дня.</p>'
            ),
            'email': 'info@trading2d.com',
            'phone': '+38 (044) 123-45-67',
            'address': 'Україна',
        }


class ProtectedPageQuerySet(models.QuerySet):
    def delete(self):
        return 0, {}


class Page(TranslatableMixin, models.Model):
    slug = models.SlugField(
        max_length=64,
        unique=True,
        editable=False,
        choices=page_slug_choices(),
        verbose_name='Ключ сторінки',
    )
    title = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255, blank=True, verbose_name='Заголовок (RU)')
    title_en = models.CharField(max_length=255, blank=True, verbose_name='Заголовок (EN)')
    description = models.TextField(blank=True, default='')
    description_ru = models.TextField(blank=True, verbose_name='Опис (RU)')
    description_en = models.TextField(blank=True, verbose_name='Опис (EN)')

    objects = ProtectedPageQuerySet.as_manager()

    class Meta:
        verbose_name = 'Інформаційна сторінка'
        verbose_name_plural = 'Інформаційні сторінки'
        ordering = ['slug']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        spec = SYSTEM_PAGES_BY_SLUG.get(self.slug)
        if spec is None:
            return '/'
        return reverse(spec.url_name)

    def delete(self, *args, **kwargs):
        return

    @classmethod
    def load(cls, slug):
        spec = SYSTEM_PAGES_BY_SLUG[slug]
        obj, _ = cls.objects.get_or_create(
            slug=spec.slug,
            defaults={
                'title': spec.title,
                'description': spec.default_html,
            },
        )
        return obj
