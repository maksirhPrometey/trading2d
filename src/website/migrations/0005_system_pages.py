from django.db import migrations, models


SLUG_CHOICES = [
    ('about', 'Про нас'),
    ('delivery', 'Доставка та оплата'),
    ('privacy', 'Політика конфіденційності'),
    ('terms', 'Договір оферти'),
]


def seed_system_pages(apps, schema_editor):
    Page = apps.get_model('website', 'Page')
    Page.objects.all().delete()
    from src.website.pages import SYSTEM_PAGES

    Page.objects.bulk_create(
        [
            Page(slug=spec.slug, title=spec.title, description=spec.default_html)
            for spec in SYSTEM_PAGES
        ]
    )


def normalize_contact_page(apps, schema_editor):
    ContactPage = apps.get_model('website', 'ContactPage')
    first = ContactPage.objects.order_by('pk').first()
    if first is None:
        return
    if first.pk != 1:
        ContactPage.objects.filter(pk=1).delete()
        ContactPage.objects.filter(pk=first.pk).update(pk=1)
    ContactPage.objects.exclude(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_admin_verbose_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='slug',
            field=models.SlugField(db_index=False, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='contactpage',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.RunPython(seed_system_pages, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='page',
            name='slug',
            field=models.SlugField(
                choices=SLUG_CHOICES,
                editable=False,
                max_length=64,
                unique=True,
                verbose_name='Ключ сторінки',
            ),
        ),
        migrations.AlterModelOptions(
            name='page',
            options={
                'ordering': ['slug'],
                'verbose_name': 'Інформаційна сторінка',
                'verbose_name_plural': 'Інформаційні сторінки',
            },
        ),
        migrations.RunPython(normalize_contact_page, migrations.RunPython.noop),
    ]
