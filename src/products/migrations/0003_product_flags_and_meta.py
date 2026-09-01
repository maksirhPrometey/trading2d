# Generated manually

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='in_stock',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='is_bestseller',
            field=models.BooleanField(default=False, verbose_name='Хіт продажу'),
        ),
        migrations.AddField(
            model_name='product',
            name='is_new',
            field=models.BooleanField(default=False, verbose_name='Новинка'),
        ),
        migrations.AddField(
            model_name='product',
            name='old_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='images',
            field=models.ManyToManyField(blank=True, related_name='products', to='products.gallery'),
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-created_at']},
        ),
    ]
