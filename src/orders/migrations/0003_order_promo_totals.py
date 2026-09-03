import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


def fill_totals(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    Order.objects.filter(total=0).update(total=models.F('subtotal'))


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_accounts_profile_and_order_user'),
        ('promos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discount_amount',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='discount_percent',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='promo',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='orders',
                to='promos.promocode',
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='promo_code',
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.RunPython(fill_totals, migrations.RunPython.noop),
    ]
