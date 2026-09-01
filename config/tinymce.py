"""Конфігурація django-tinymce для Unfold-адмінки."""

TINYMCE_DEFAULT_CONFIG = {
    'height': 400,
    'menubar': False,
    'plugins': 'link lists image code autoresize',
    'toolbar': (
        'undo redo | blocks | bold italic underline | '
        'bullist numlist | link image | code'
    ),
    'block_formats': 'Параграф=p; Заголовок 2=h2; Заголовок 3=h3; Цитата=blockquote',
    'toolbar_mode': 'sliding',
    'min_height': 280,
    'max_height': 720,
    'content_css': False,
    'skin': 'oxide',
    'promotion': False,
    'branding': False,
    'browser_spellcheck': True,
    'relative_urls': False,
    'remove_script_host': False,
    'convert_urls': True,
    'content_style': (
        'body { font-family: Lato, -apple-system, BlinkMacSystemFont, '
        "'Segoe UI', sans-serif; font-size: 16px; line-height: 1.5; "
        'color: #1A1A1A; }'
    ),
}

TINYMCE_COMPRESSOR = False

TINYMCE_EXTRA_MEDIA = {
    'css': {
        'all': ['admin/css/tinymce_unfold.css'],
    },
}
