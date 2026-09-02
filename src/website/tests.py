from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from src.website.models import ContactPage, Page
from src.website.pages import SYSTEM_SLUGS
from src.website.services import ensure_system_pages


class SystemPagesTests(TestCase):
    def test_ensure_pages_is_idempotent(self):
        self.assertEqual(Page.objects.count(), 4)
        created, existing = ensure_system_pages()
        self.assertEqual(len(created), 0)
        self.assertEqual(len(existing), 4)
        self.assertEqual(set(Page.objects.values_list('slug', flat=True)), SYSTEM_SLUGS)

    def test_command_does_not_overwrite_content(self):
        page = Page.objects.get(slug='about')
        page.description = '<p>Кастомний текст</p>'
        page.save(update_fields=['description'])
        call_command('ensure_pages', verbosity=0)
        page.refresh_from_db()
        self.assertEqual(page.description, '<p>Кастомний текст</p>')

    def test_page_cannot_be_deleted(self):
        page = Page.objects.get(slug='delivery')
        pk = page.pk
        page.delete()
        self.assertTrue(Page.objects.filter(pk=pk).exists())
        Page.objects.all().delete()
        self.assertEqual(Page.objects.count(), 4)


    def test_info_pages_render_from_db(self):
        Page.objects.filter(slug='about').update(title='Про магазин')
        response = self.client.get(reverse('about_us'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Про магазин')

    def test_contact_is_singleton(self):
        first = ContactPage.load()
        second = ContactPage.load()
        self.assertEqual(first.pk, 1)
        self.assertEqual(second.pk, 1)
        first.delete()
        self.assertTrue(ContactPage.objects.filter(pk=1).exists())


class SystemPagesAdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            'admin',
            'admin@example.com',
            'password12345',
        )
        self.client.force_login(self.user)

    def test_admin_tab_opens_editor(self):
        url = reverse('admin:website_page_about')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Про нас')

    def test_admin_forbids_add_and_delete(self):
        add_url = reverse('admin:website_page_add')
        response = self.client.get(add_url)
        self.assertEqual(response.status_code, 403)
        page = Page.objects.get(slug='terms')
        delete_url = reverse('admin:website_page_delete', args=[page.pk])
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 403)


class HomeShowcaseTests(TestCase):
    def setUp(self):
        from src.products.models import Category, Product
        from src.website.models import HomeShowcaseItem, MainPage

        self.category = Category.objects.create(name='Тест', description='')
        self.flagged = Product.objects.create(
            name='Прапорець хіт',
            description='d',
            category=self.category,
            is_bestseller=True,
        )
        self.picked = Product.objects.create(
            name='Обраний хіт',
            description='d',
            category=self.category,
        )
        self.page = MainPage.load()
        HomeShowcaseItem.objects.create(
            page=self.page,
            product=self.picked,
            slot=HomeShowcaseItem.Slot.BESTSELLER,
            order=0,
        )

    def test_home_uses_showcase_not_product_flags(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Обраний хіт')
        self.assertNotContains(response, 'Прапорець хіт')

    def test_admin_saves_both_slots_without_unique_clash(self):
        from src.products.models import Product
        from src.website.models import HomeShowcaseItem

        other = Product.objects.create(
            name='Новинка з адмінки',
            description='d',
            category=self.category,
        )
        user = User.objects.create_superuser(
            'editor',
            'editor@example.com',
            'password12345',
        )
        self.client.force_login(user)
        response = self.client.post(
            reverse('admin:website_mainpage_change', args=[self.page.pk]),
            {
                'title': 'TRADING 2D',
                'description': '',
                'bestsellers-TOTAL_FORMS': '1',
                'bestsellers-INITIAL_FORMS': '1',
                'bestsellers-MIN_NUM_FORMS': '0',
                'bestsellers-MAX_NUM_FORMS': '8',
                'bestsellers-0-id': str(
                    HomeShowcaseItem.objects.get(
                        slot=HomeShowcaseItem.Slot.BESTSELLER
                    ).pk
                ),
                'bestsellers-0-page': str(self.page.pk),
                'bestsellers-0-product': str(self.picked.pk),
                'bestsellers-0-order': '0',
                'new_arrivals-TOTAL_FORMS': '1',
                'new_arrivals-INITIAL_FORMS': '0',
                'new_arrivals-MIN_NUM_FORMS': '0',
                'new_arrivals-MAX_NUM_FORMS': '8',
                'new_arrivals-0-page': str(self.page.pk),
                'new_arrivals-0-product': str(other.pk),
                'new_arrivals-0-order': '0',
                '_save': 'Зберегти',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            HomeShowcaseItem.objects.filter(
                product=other,
                slot=HomeShowcaseItem.Slot.NEW_ARRIVAL,
            ).exists()
        )
        self.assertEqual(HomeShowcaseItem.objects.count(), 2)


class LocaleSelectionTests(TestCase):
    def _content_lang(self, response):
        return (response.headers.get('Content-Language') or '')[:2]

    def test_home_stays_uk_when_browser_is_russian(self):
        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='ru-RU,ru;q=0.9,en;q=0.8')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._content_lang(response), 'uk')
        self.assertContains(response, 'data-lang-menu')
        self.assertContains(response, 'lang-toggle-code')
        self.assertContains(response, '>УК<')
        self.assertNotContains(response, 'data-lang-select')
        self.assertNotContains(response, 'id="lang-select"')

    def test_ru_cookie_does_not_switch_unprefixed_home(self):
        from django.conf import settings as django_settings

        self.client.cookies[django_settings.LANGUAGE_COOKIE_NAME] = 'ru'
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._content_lang(response), 'uk')

    def test_explicit_ru_prefix_still_works(self):
        response = self.client.get('/ru/', HTTP_ACCEPT_LANGUAGE='uk')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._content_lang(response), 'ru')
        self.assertContains(response, '>РУ<')

    def test_set_language_to_en_prefixes_url(self):
        response = self.client.post(
            reverse('set_language'),
            {'language': 'en', 'next': '/'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('/en'))

    def test_set_language_from_en_home_to_uk(self):
        response = self.client.post(
            reverse('set_language'),
            {'language': 'uk', 'next': '/en/'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')

    def test_set_language_from_en_catalog_to_ru(self):
        response = self.client.post(
            reverse('set_language'),
            {'language': 'ru', 'next': '/en/catalog/'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/ru/catalog/')

    def test_set_language_from_ru_to_en(self):
        response = self.client.post(
            reverse('set_language'),
            {'language': 'en', 'next': '/ru/'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/en/')
