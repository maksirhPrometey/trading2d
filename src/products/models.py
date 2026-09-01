from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models

from src.i18n import TranslatableMixin
from src.products.utils import ukrainian_slugify, validate_max_file_size

ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']


class Gallery(models.Model):
    image = models.ImageField(
        upload_to='gallery/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_IMAGE_EXTENSIONS),
            validate_max_file_size,
        ],
    )
    source_url = models.URLField(blank=True, verbose_name='Посилання на оригінал')

    class Meta:
        verbose_name = 'Зображення'
        verbose_name_plural = 'Галерея'

    def __str__(self):
        if self.image:
            return self.image.name
        return self.source_url or f'Зображення #{self.pk or "new"}'


class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренди'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = ukrainian_slugify(self.name, fallback=f'brand-{self.pk or "new"}')
        super().save(*args, **kwargs)


class Category(TranslatableMixin, models.Model):
    name = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255, blank=True, verbose_name='Назва (RU)')
    name_en = models.CharField(max_length=255, blank=True, verbose_name='Назва (EN)')
    description = models.TextField()
    description_ru = models.TextField(blank=True, verbose_name='Опис (RU)')
    description_en = models.TextField(blank=True, verbose_name='Опис (EN)')
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='Батьківська категорія',
    )
    external_id = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        verbose_name='Зовнішній ID (з фіда постачальника)',
    )

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse

        return f'{reverse("catalog")}?category={self.pk}'


class Product(TranslatableMixin, models.Model):
    name = models.CharField(max_length=255, db_index=True)
    name_ru = models.CharField(max_length=255, blank=True, verbose_name='Назва (RU)')
    name_en = models.CharField(max_length=255, blank=True, verbose_name='Назва (EN)')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    sku = models.CharField(max_length=64, blank=True, verbose_name='Артикул')
    description = models.TextField()
    description_ru = models.TextField(blank=True, verbose_name='Опис (RU)')
    description_en = models.TextField(blank=True, verbose_name='Опис (EN)')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        db_index=True,
        validators=[MinValueValidator(0)],
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    in_stock = models.BooleanField(default=True, db_index=True)
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name='Кількість на складі')
    meta_title = models.CharField(max_length=255, blank=True, verbose_name='SEO: заголовок сторінки')
    meta_title_ru = models.CharField(max_length=255, blank=True, verbose_name='SEO: заголовок (RU)')
    meta_title_en = models.CharField(max_length=255, blank=True, verbose_name='SEO: заголовок (EN)')
    meta_description = models.CharField(max_length=320, blank=True, verbose_name='SEO: опис сторінки')
    meta_description_ru = models.CharField(max_length=320, blank=True, verbose_name='SEO: опис (RU)')
    meta_description_en = models.CharField(max_length=320, blank=True, verbose_name='SEO: опис (EN)')
    is_bestseller = models.BooleanField(default=False, verbose_name='Хіт продажу')
    is_new = models.BooleanField(default=False, verbose_name='Новинка')
    created_at = models.DateTimeField(auto_now_add=True)
    images = models.ManyToManyField(Gallery, related_name='products', blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(
        Brand,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products',
        verbose_name='Бренд',
    )
    external_id = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        verbose_name='Зовнішній ID (з фіда постачальника)',
    )
    vendor_code = models.CharField(max_length=128, blank=True, verbose_name='Код виробника')
    barcode = models.CharField(max_length=64, blank=True, verbose_name='Штрихкод (EAN)')
    source_url = models.URLField(blank=True, verbose_name='Посилання на оригінал')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name='product_price_non_negative',
            ),
        ]
        indexes = [
            models.Index(fields=['category', 'in_stock']),
            models.Index(fields=['is_bestseller']),
            models.Index(fields=['is_new']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse('product_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._build_unique_slug()
        super().save(*args, **kwargs)
        if not self.sku:
            self.sku = f'TR-2D-{self.pk:04d}'
            super().save(update_fields=['sku'])

    def _build_unique_slug(self):
        base = ukrainian_slugify(self.name, fallback=f'product-{self.pk or "new"}')
        slug = base
        counter = 1
        while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f'{base}-{counter}'
            counter += 1
        return slug

    @property
    def primary_image(self):
        return self.images.first()

    @property
    def discount_percent(self):
        if not self.old_price or self.old_price <= self.price:
            return None
        return int((self.old_price - self.price) / self.old_price * 100)

    @property
    def savings_amount(self):
        if not self.old_price or self.old_price <= self.price:
            return None
        return self.old_price - self.price


class ProductAttribute(TranslatableMixin, models.Model):
    product = models.ForeignKey(Product, related_name='attributes', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name='Назва характеристики')
    name_ru = models.CharField(max_length=255, blank=True, verbose_name='Назва (RU)')
    name_en = models.CharField(max_length=255, blank=True, verbose_name='Назва (EN)')
    value = models.CharField(max_length=500, verbose_name='Значення')
    value_ru = models.CharField(max_length=500, blank=True, verbose_name='Значення (RU)')
    value_en = models.CharField(max_length=500, blank=True, verbose_name='Значення (EN)')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Характеристика товару'
        verbose_name_plural = 'Характеристики товару'
        ordering = ['order', 'pk']

    def __str__(self):
        return f'{self.name}: {self.value}'