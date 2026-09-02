from urllib.parse import urlsplit, urlunsplit

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import translate_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import check_for_language
from django.views.i18n import LANGUAGE_QUERY_PARAMETER


def strip_language_prefix(path):
    """Прибирає /en/ або /ru/, щоб resolve() бачив шлях без префікса.

    set_language POST іде на /i18n/setlang/ (поза i18n_patterns), тож
    активна мова — LANGUAGE_CODE. Django resolve('/en/…') тоді 404, і
    translate_url лишає next без змін — перемикач «не працює».
    """
    if not path:
        return '/'
    if not path.startswith('/'):
        path = f'/{path}'
    default = (settings.LANGUAGE_CODE or 'uk')[:2]
    for code, _unused in settings.LANGUAGES:
        code = code[:2]
        if code == default:
            continue
        prefix = f'/{code}/'
        if path.startswith(prefix):
            remainder = path[len(prefix):]
            return f'/{remainder}' if remainder else '/'
        if path == f'/{code}':
            return '/'
    return path


def set_language(request):
    next_url = request.POST.get('next', request.GET.get('next'))
    if (
        next_url or request.accepts('text/html')
    ) and not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = request.META.get('HTTP_REFERER')
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = '/'
    response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=204)
    if request.method == 'POST':
        lang_code = request.POST.get(LANGUAGE_QUERY_PARAMETER)
        if lang_code and check_for_language(lang_code):
            if next_url:
                parsed = urlsplit(next_url)
                stripped = strip_language_prefix(parsed.path or '/')
                next_for_translate = urlunsplit(
                    ('', '', stripped, parsed.query, parsed.fragment)
                )
                next_trans = translate_url(next_for_translate, lang_code)
                response = HttpResponseRedirect(next_trans)
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                lang_code,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )
    return response
