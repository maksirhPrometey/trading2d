from django.utils.translation import get_language

TRANSLATION_LANGS = ('ru', 'en')


class TranslatableMixin:
    """Повертає поле поточної мови (uk — базове, ru/en — суфікс _ru/_en).
    Якщо переклад порожній, падає назад на українське значення."""

    def loc(self, field):
        lang = (get_language() or 'uk')[:2]
        if lang in TRANSLATION_LANGS:
            translated = getattr(self, f'{field}_{lang}', None)
            if translated:
                return translated
        return getattr(self, field) or ''
