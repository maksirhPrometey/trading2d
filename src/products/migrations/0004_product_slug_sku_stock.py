from django.db import migrations, models
from django.utils.text import slugify


def populate_product_slugs_and_skus(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    for product in Product.objects.all():
        updated_fields = []

        if not product.slug:
            base = slugify(product.name) or f'product-{product.pk}'
            slug = base
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=product.pk).exists():
                slug = f'{base}-{counter}'
                counter += 1
            product.slug = slug
            updated_fields.append('slug')

        if not product.sku:
            product.sku = f'TR-2D-{product.pk:04d}'
            updated_fields.append('sku')

        if updated_fields:
            product.save(update_fields=updated_fields)


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_product_flags_and_meta'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sku',
            field=models.CharField(blank=True, max_length=64, verbose_name='Артикул'),
        ),
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='product',
            name='stock_quantity',
            field=models.PositiveIntegerField(default=0, verbose_name='Кількість на складі'),
        ),
        migrations.RunPython(populate_product_slugs_and_skus, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]
