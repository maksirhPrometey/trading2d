import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0002_accounts_profile_and_order_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=32, unique=True, verbose_name='Код')),
                ('discount_percent', models.PositiveSmallIntegerField(
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(100),
                    ],
                    verbose_name='Знижка, %',
                )),
                ('is_active', models.BooleanField(default=True, verbose_name='Активний')),
                ('valid_from', models.DateTimeField(blank=True, null=True, verbose_name='Діє з')),
                ('valid_until', models.DateTimeField(blank=True, null=True, verbose_name='Діє до')),
                ('min_order_amount', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    max_digits=10,
                    null=True,
                    validators=[django.core.validators.MinValueValidator(0)],
                    verbose_name='Мін. сума кошика',
                )),
                ('max_uses', models.PositiveIntegerField(
                    blank=True,
                    help_text='Порожньо — без загального ліміту.',
                    null=True,
                    verbose_name='Ліміт використань',
                )),
                ('max_uses_per_customer', models.PositiveIntegerField(
                    blank=True,
                    help_text='Порожньо — без ліміту на акаунт / сесію.',
                    null=True,
                    verbose_name='Ліміт на покупця',
                )),
                ('used_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='Використано')),
                ('note', models.CharField(blank=True, max_length=255, verbose_name='Нотатка')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Промокод',
                'verbose_name_plural': 'Промокоди',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PromoRedemption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, db_index=True, max_length=40)),
                ('phone', models.CharField(blank=True, max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='promo_redemption',
                    to='orders.order',
                )),
                ('promo', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='redemptions',
                    to='promos.promocode',
                )),
                ('user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='promo_redemptions',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Використання промокоду',
                'verbose_name_plural': 'Використання промокодів',
            },
        ),
        migrations.AddConstraint(
            model_name='promoredemption',
            constraint=models.UniqueConstraint(fields=('promo', 'order'), name='uniq_promo_order'),
        ),
    ]
