"""Docker / Droplet — TLS у nginx, Gunicorn лише HTTP (django-docker-ssl).

HTTP-first (деплой по IP до certbot): SESSION/CSRF_COOKIE_SECURE=False, HSTS=0.
Після HTTPS у .env: SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True,
SECURE_HSTS_SECONDS=31536000.
"""
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

from config.env import env, env_bool, env_list
from config.settings.base import *  # noqa: F401, F403


class ForgivingManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """Не ValueError, якщо файл відсутній у staticfiles.json (ERR-02)."""

    manifest_strict = False

    def hashed_name(self, name, content=None, filename=None):
        try:
            return super().hashed_name(name, content=content, filename=filename)
        except ValueError:
            return name


DEBUG = False

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', [])
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS', [])

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# TLS завершується в nginx; інакше healthcheck на :8000 отримує 301.
SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', False)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', False)
SESSION_COOKIE_SAMESITE = env('SESSION_COOKIE_SAMESITE', 'Lax')
CSRF_COOKIE_SAMESITE = env('CSRF_COOKIE_SAMESITE', 'Lax')
SECURE_HSTS_SECONDS = int(env('SECURE_HSTS_SECONDS', '0') or 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', False)
SECURE_HSTS_PRELOAD = env_bool('SECURE_HSTS_PRELOAD', False)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB', env('DB_NAME', 'trading2d')),
        'USER': env('POSTGRES_USER', env('DB_USER', 'trading2d')),
        'PASSWORD': env('POSTGRES_PASSWORD', env('DB_PASSWORD', '')),
        'HOST': env('POSTGRES_HOST', env('DB_HOST', 'db')),
        'PORT': env('POSTGRES_PORT', env('DB_PORT', '5432')),
        'CONN_MAX_AGE': 60,
    }
}

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'config.settings.docker.ForgivingManifestStaticFilesStorage',
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': env('DJANGO_LOG_LEVEL', 'INFO'),
    },
}

EMAIL_BACKEND = env('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', '')
EMAIL_PORT = int(env('EMAIL_PORT', '587') or 587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', 'noreply@trading2d.com')
