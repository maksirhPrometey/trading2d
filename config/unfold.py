"""Конфігурація django-unfold. Сайдбар дзеркалить публічне меню сайту."""

from django.urls import reverse_lazy

UNFOLD = {
    'SITE_TITLE': 'TRADING 2D',
    'SITE_HEADER': 'TRADING 2D — Адмінпанель',
    'SITE_SUBHEADER': 'Каталог і замовлення',
    'SITE_URL': '/',
    'SITE_SYMBOL': 'storefront',
    'SHOW_HISTORY': True,
    'SHOW_VIEW_ON_SITE': True,
    'SHOW_BACK_BUTTON': True,
    'SITE_DROPDOWN': [
        {
            'icon': 'public',
            'title': 'Відкрити сайт',
            'link': '/',
        },
    ],
    'COLORS': {
        'primary': {
            '50': 'oklch(97.5% 0.002 90)',
            '100': 'oklch(94.5% 0.003 90)',
            '200': 'oklch(90% 0.004 90)',
            '300': 'oklch(83% 0.005 90)',
            '400': 'oklch(64% 0.006 90)',
            '500': 'oklch(45% 0.006 90)',
            '600': 'oklch(35% 0.006 90)',
            '700': 'oklch(28% 0.005 90)',
            '800': 'oklch(21% 0.004 90)',
            '900': 'oklch(16% 0.003 90)',
            '950': 'oklch(12% 0.002 90)',
        },
    },
    'COMMAND': {
        'search_models': True,
        'show_history': True,
    },
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': False,
        'navigation': [
            {
                'title': 'Налаштування',
                'separator': False,
                'collapsible': False,
                'items': [
                    {
                        'title': 'Налаштування сайту',
                        'icon': 'settings',
                        'link': reverse_lazy('admin:website_sitesettings_changelist'),
                    },
                ],
            },
            {
                'title': 'Сторінки сайту',
                'separator': True,
                'collapsible': False,
                'items': [
                    {
                        'title': 'Головна',
                        'icon': 'home',
                        'link': reverse_lazy('admin:website_mainpage_changelist'),
                    },
                    {
                        'title': 'Про нас',
                        'icon': 'info',
                        'link': reverse_lazy('admin:website_page_about'),
                    },
                    {
                        'title': 'Доставка та оплата',
                        'icon': 'local_shipping',
                        'link': reverse_lazy('admin:website_page_delivery'),
                    },
                    {
                        'title': 'Політика конфіденційності',
                        'icon': 'privacy_tip',
                        'link': reverse_lazy('admin:website_page_privacy'),
                    },
                    {
                        'title': 'Договір оферти',
                        'icon': 'gavel',
                        'link': reverse_lazy('admin:website_page_terms'),
                    },
                    {
                        'title': 'Контакти',
                        'icon': 'call',
                        'link': reverse_lazy('admin:website_contactpage_changelist'),
                    },
                ],
            },
            {
                'title': 'Каталог',
                'separator': True,
                'collapsible': False,
                'items': [
                    {
                        'title': 'Товари',
                        'icon': 'inventory_2',
                        'link': reverse_lazy('admin:products_product_changelist'),
                    },
                    {
                        'title': 'Категорії',
                        'icon': 'category',
                        'link': reverse_lazy('admin:products_category_changelist'),
                    },
                    {
                        'title': 'Бренди',
                        'icon': 'sell',
                        'link': reverse_lazy('admin:products_brand_changelist'),
                    },
                    {
                        'title': 'Галерея',
                        'icon': 'photo_library',
                        'link': reverse_lazy('admin:products_gallery_changelist'),
                    },
                ],
            },
            {
                'title': 'Продажі',
                'separator': True,
                'collapsible': False,
                'items': [
                    {
                        'title': 'Замовлення',
                        'icon': 'receipt_long',
                        'link': reverse_lazy('admin:orders_order_changelist'),
                    },
                    {
                        'title': 'Кошики',
                        'icon': 'shopping_cart',
                        'link': reverse_lazy('admin:cart_cart_changelist'),
                    },
                ],
            },
            {
                'title': 'Користувачі',
                'separator': True,
                'collapsible': True,
                'items': [
                    {
                        'title': 'Користувачі',
                        'icon': 'group',
                        'link': reverse_lazy('admin:auth_user_changelist'),
                    },
                    {
                        'title': 'Групи',
                        'icon': 'admin_panel_settings',
                        'link': reverse_lazy('admin:auth_group_changelist'),
                    },
                ],
            },
        ],
    },
}
