from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def healthz(_request):
    return HttpResponse('ok', content_type='text/plain; charset=utf-8')


@require_GET
def robots_txt(_request):
    domain = getattr(settings, 'SITE_DOMAIN', 'trading2d.com')
    protocol = getattr(settings, 'SITE_PROTOCOL', 'https')
    sitemap_url = f'{protocol}://{domain}/sitemap.xml'
    body = '\n'.join([
        'User-agent: *',
        'Allow: /',
        'Disallow: /cart/',
        'Disallow: /checkout/',
        'Disallow: /wishlist/',
        'Disallow: /orders/',
        f'Sitemap: {sitemap_url}',
        '',
    ])
    return HttpResponse(body, content_type='text/plain; charset=utf-8')
