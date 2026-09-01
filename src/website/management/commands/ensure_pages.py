from django.core.management.base import BaseCommand

from src.website.services import ensure_system_pages


class Command(BaseCommand):
    help = (
        'Створює записи інфо-сторінок (про нас, доставка, privacy, оферта), '
        'якщо їх ще немає. Існуючий контент не змінює.'
    )

    def handle(self, *args, **options):
        created, existing = ensure_system_pages()
        for page in created:
            self.stdout.write(self.style.SUCCESS(f'Створено: {page.slug} — {page.title}'))
        for page in existing:
            self.stdout.write(f'Вже є: {page.slug} — {page.title}')
        self.stdout.write(
            self.style.SUCCESS(
                f'Готово. Створено {len(created)}, без змін {len(existing)}.'
            )
        )
