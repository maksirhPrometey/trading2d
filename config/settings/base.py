"""
Спільні налаштування Django для config project.
Середовище-специфічні файли (dev.py / prod.py) успадковують і перевизначають
частину цих значень.
"""
from pathlib import Path

from config.env import env, env_bool, env_list
from config.tinymce import TINYMCE_COMPRESSOR, TINYMCE_DEFAULT_CONFIG, TINYMCE_EXTRA_MEDIA  # noqa: F401
from config.unfold import UNFOLD  # noqa: F401

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env('SECRET_KEY')

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'tinymce',
    'src.products.apps.ProductsConfig',
    'src.website.apps.WebsiteConfig',
    'src.accounts.apps.AccountsConfig',
    'src.cart.apps.CartConfig',
    'src.wishlist.apps.WishlistConfig',
    'src.orders.apps.OrdersConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'src.website.middleware.ExplicitLocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'src.website.context_processors.site_settings',
                'src.cart.context_processors.cart',
                'src.wishlist.context_processors.wishlist',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'uk'

LANGUAGES = [
    ('uk', 'Українська'),
    ('ru', 'Русский'),
    ('en', 'English'),
]

LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365
LANGUAGE_COOKIE_SAMESITE = 'Lax'
LANGUAGE_COOKIE_HTTPONLY = True

LOCALE_PATHS = [BASE_DIR / 'locale']

TIME_ZONE = 'Europe/Kyiv'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'src' / 'core' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Адмінка — ніколи дефолтний /admin/ (ERR-132). Порожнє і літерал admin → manage/
_admin_path = (env('ADMIN_URL', 'manage') or 'manage').strip().strip('/')
if not _admin_path or _admin_path.lower() == 'admin':
    _admin_path = 'manage'
ADMIN_URL = f'{_admin_path}/'
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:profile'
LOGOUT_REDIRECT_URL = 'home'

X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# --- Nova Poshta (Фаза 5.3) ---
NOVA_POSHTA_API_KEY = env('NOVA_POSHTA_API_KEY', '')
NOVA_POSHTA_API_URL = env('NOVA_POSHTA_API_URL', 'https://api.novaposhta.ua/v2.0/json/')

# --- Оплата (Фаза 5.4) ---
LIQPAY_PUBLIC_KEY = env('LIQPAY_PUBLIC_KEY', '')
LIQPAY_PRIVATE_KEY = env('LIQPAY_PRIVATE_KEY', '')
LIQPAY_SANDBOX = env_bool('LIQPAY_SANDBOX', True)

SITE_DOMAIN = env('SITE_DOMAIN', 'localhost:8000')
SITE_PROTOCOL = env('SITE_PROTOCOL', 'http')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', 'noreply@trading2d.com')
