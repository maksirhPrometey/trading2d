"""Ідемпотентне створення системних сторінок. Не перезаписує вже відредагований контент."""
from src.website.models import Page
from src.website.pages import SYSTEM_PAGES


def ensure_system_pages():
    created = []
    existing = []
    for spec in SYSTEM_PAGES:
        obj, was_created = Page.objects.get_or_create(
            slug=spec.slug,
            defaults={
                'title': spec.title,
                'description': spec.default_html,
            },
        )
        if was_created:
            created.append(obj)
        else:
            existing.append(obj)
    return created, existing
