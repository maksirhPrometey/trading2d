from django.conf import settings
from django.conf.urls.i18n import is_language_prefix_patterns_used
from django.middleware.locale import LocaleMiddleware
from django.utils import translation


class ExplicitLocaleMiddleware(LocaleMiddleware):
    """Мова лише з URL-префікса. Без префікса — LANGUAGE_CODE (uk).

    LocaleMiddleware інакше бере Accept-Language: браузер ru відкриває
    російську вітрину, хоча користувач мову не обирав.
    """

    def process_request(self, request):
        language_from_path = translation.get_language_from_path(request.path_info)
        language = language_from_path or settings.LANGUAGE_CODE
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        language = translation.get_language()
        language_from_path = translation.get_language_from_path(request.path_info)
        urlconf = getattr(request, 'urlconf', settings.ROOT_URLCONF)
        (
            i18n_patterns_used,
            prefixed_default_language,
        ) = is_language_prefix_patterns_used(urlconf)

        if (
            response.status_code == 404
            and not language_from_path
            and i18n_patterns_used
            and prefixed_default_language
        ):
            return super().process_response(request, response)

        response.headers.setdefault('Content-Language', language)
        return response
