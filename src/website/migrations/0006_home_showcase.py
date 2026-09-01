import django.db.models.deletion
from django.db import migrations, models


def seed_showcase_from_flags(apps, schema_editor):
    MainPage = apps.get_model('website', 'MainPage')
    Product = apps.get_model('products', 'Product')
    HomeShowcaseItem = apps.get_model('website', 'HomeShowcaseItem')
    page = MainPage.objects.order_by('pk').first()
    if page is None:
        return
    bestsellers = Product.objects.filter(is_bestseller=True).order_by('-created_at')[:8]
    news = Product.objects.filter(is_new=True).order_by('-created_at')[:8]
    items = [
        HomeShowcaseItem(page_id=page.pk, product_id=product.pk, slot='bestseller', order=index)
        for index, product in enumerate(bestsellers)
    ]
    items.extend(
        HomeShowcaseItem(page_id=page.pk, product_id=product.pk, slot='new_arrival', order=index)
        for index, product in enumerate(news)
    )
    if items:
        HomeShowcaseItem.objects.bulk_create(items)


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_product_meta_description_product_meta_title_and_more'),
        ('website', '0005_system_pages'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomeShowcaseItem',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'slot',
                    models.CharField(
                        choices=[
                            ('bestseller', 'Хіти продажу'),
                            ('new_arrival', 'Новинки'),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    'order',
                    models.PositiveSmallIntegerField(default=0, verbose_name='Порядок'),
                ),
                (
                    'page',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='showcase_items',
                        to='website.mainpage',
                    ),
                ),
                (
                    'product',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='products.product',
                        verbose_name='Товар',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Товар на головній',
                'verbose_name_plural': 'Товари на головній',
                'ordering': ['slot', 'order', 'pk'],
                'constraints': [
                    models.UniqueConstraint(
                        fields=('page', 'product', 'slot'),
                        name='unique_home_showcase_product_slot',
                    ),
                ],
            },
        ),
        migrations.RunPython(seed_showcase_from_flags, migrations.RunPython.noop),
    ]
