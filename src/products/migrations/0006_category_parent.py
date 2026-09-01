from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_brand_category_external_id_gallery_source_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.CASCADE,
                related_name='children',
                to='products.category',
                verbose_name='Батьківська категорія',
            ),
        ),
    ]
