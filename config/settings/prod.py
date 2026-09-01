"""Налаштування для продакшн-середовища.

Усі значення читаються з env — жодних секретів у коді.
Обов'язкові змінні середовища: SECRET_KEY, ALLOWED_HOSTS, DB_NAME,
DB_USER, DB_PASSWORD, DB_HOST.
"""
from config.settings.base import *  # noqa: F401,F403
from config.env import env, env_bool, env_list

DEBUG = False

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', [])
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS', [])

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', 'trading2d'),
        'USER': env('DB_USER', 'trading2d'),
        'PASSWORD': env('DB_PASSWORD', ''),
        'HOST': env('DB_HOST', 'localhost'),
        'PORT': env('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,
    }
}

# --- HTTPS / cookies / HSTS ---
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 днів
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- Статика через WhiteNoise (додати в MIDDLEWARE після SecurityMiddleware) ---
MIDDLEWARE = list(MIDDLEWARE)  # noqa: F405
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# --- Логування помилок у stdout (перехоплюється systemd/docker/hosting) ---
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
EMAIL_PORT = int(env('EMAIL_PORT', '587'))
EMAIL_HOST_USER = env('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
