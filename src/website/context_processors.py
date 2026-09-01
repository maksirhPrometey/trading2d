from src.website.models import ContactPage, SiteSettings


def site_settings(request):
    """Дає доступ до SiteSettings і ContactPage (лого, favicon, телефон)
    у будь-якому шаблоні, щоб не хардкодити ці значення в header.html/base.html."""
    return {
        'site_settings': SiteSettings.objects.first(),
        'contact_info': ContactPage.load(),
    }
