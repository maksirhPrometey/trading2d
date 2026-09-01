"""Налаштування для локальної розробки."""
from config.settings.base import *  # noqa: F401,F403
from config.env import env, env_bool, env_list

SECRET_KEY = env('SECRET_KEY', 'dev-only-insecure-key-do-not-use-in-prod')

DEBUG = env_bool('DEBUG', True)

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', ['localhost', '127.0.0.1'])

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

UNFOLD['ENVIRONMENT'] = ('Dev', 'warning')  # noqa: F405
