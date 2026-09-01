"""Санітизація HTML з TinyMCE (SEC-04)."""

import bleach
from django.utils.html import linebreaks
from django.utils.safestring import mark_safe

ALLOWED_TAGS = [
    'p',
    'br',
    'strong',
    'b',
    'em',
    'i',
    'u',
    'ul',
    'ol',
    'li',
    'a',
    'h2',
    'h3',
    'blockquote',
    'img',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'width', 'height'],
}


def sanitize_html(raw: str) -> str:
    if not raw:
        return ''
    return bleach.clean(
        raw,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=['http', 'https', 'mailto'],
        strip=True,
    )


def render_richtext(value) -> str:
    if not value:
        return ''
    text = str(value)
    if '<' not in text:
        return mark_safe(linebreaks(text))
    return mark_safe(sanitize_html(text))
