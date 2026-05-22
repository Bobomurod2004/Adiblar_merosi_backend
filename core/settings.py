"""
Django settings for Adiblar Merosi project.

Production-ready configuration.
"""

import os
from pathlib import Path
from urllib.parse import urlsplit, unquote
from decouple import config, Csv


def env_to_bool(value, default=False):
    """Config matn qiymatini xavfsiz boolean ga o'tkazadi."""
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()
    if normalized in {'1', 'true', 't', 'yes', 'y', 'on', 'debug', 'dev', 'development'}:
        return True
    if normalized in {'0', 'false', 'f', 'no', 'n', 'off', 'prod', 'production', 'release'}:
        return False
    return default


def normalize_origin(value):
    """Origin qiymatidan path/oxirgi slashni olib tashlaydi."""
    if value is None:
        return ''

    cleaned = str(value).strip()
    if not cleaned:
        return ''

    parsed = urlsplit(cleaned)
    if parsed.scheme and parsed.netloc:
        return f'{parsed.scheme}://{parsed.netloc}'

    return cleaned.rstrip('/')


def parse_origins(env_key, default=''):
    """CSV ko'rinishidagi originlarni normalize qilib qaytaradi."""
    values = config(env_key, default=default, cast=Csv())
    normalized = [normalize_origin(value) for value in values]
    return [value for value in dict.fromkeys(normalized) if value]


def parse_postgres_url(value):
    """
    postgres:// yoki postgresql:// URL ni Django DB dict formatiga o'tkazadi.
    Noto'g'ri qiymat bo'lsa None qaytaradi.
    """
    if value is None:
        return None

    raw = str(value).strip()
    if not raw:
        return None

    parsed = urlsplit(raw)
    if parsed.scheme not in {'postgres', 'postgresql'} or not parsed.hostname:
        return None

    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': parsed.path.lstrip('/'),
        'USER': unquote(parsed.username or ''),
        'PASSWORD': unquote(parsed.password or ''),
        'HOST': parsed.hostname,
        'PORT': str(parsed.port or 5432),
    }


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_to_bool(config('DEBUG', default='True'), default=True)

ALLOWED_HOSTS = [host.strip() for host in config('ALLOWED_HOSTS', default='', cast=Csv()) if host.strip()]

# Render deploy/health-check holatlari uchun lokal hostlarni doim qo'shamiz.
ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])

# Render avtomatik beradigan tashqi host (agar mavjud bo'lsa)
RENDER_EXTERNAL_HOSTNAME = config('RENDER_EXTERNAL_HOSTNAME', default='').strip()
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Dublikatlarni olib tashlash
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))

# Application definition

INSTALLED_APPS = [
    # Unfold must be before django.contrib.admin
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',

    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    
    # Local apps
    'apps.common.apps.CommonConfig',
    'apps.writers.apps.WritersConfig',
    'apps.works.apps.WorksConfig',
    'apps.articles.apps.ArticlesConfig',
    'apps.users.apps.UsersConfig',
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# X_FRAME_OPTIONS = 'SAMEORIGIN'

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases
DATABASE_URL = config('DATABASE_URL', default='').strip()
DB_HOST_RAW = config('DB_HOST', default='').strip()

parsed_db = parse_postgres_url(DATABASE_URL) or parse_postgres_url(DB_HOST_RAW)

if parsed_db:
    default_database = parsed_db
else:
    default_database = {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': DB_HOST_RAW,
        'PORT': config('DB_PORT', default=''),
    }

DATABASES = {'default': default_database}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'uz-UZ'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = []
PROJECT_STATIC_DIR = os.path.join(BASE_DIR, 'static')
if os.path.isdir(PROJECT_STATIC_DIR):
    STATICFILES_DIRS.append(PROJECT_STATIC_DIR)

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = config('MEDIA_ROOT', default=os.path.join(BASE_DIR, 'media'))

# Supabase Storage (ixtiyoriy, Render uchun tavsiya)
USE_SUPABASE_STORAGE = env_to_bool(config('USE_SUPABASE_STORAGE', default='False'), default=False)
SUPABASE_URL = config('SUPABASE_URL', default='').strip()
SUPABASE_KEY = config('SUPABASE_KEY', default='').strip()
SUPABASE_SERVICE_ROLE_KEY = config('SUPABASE_SERVICE_ROLE_KEY', default='').strip()
SUPABASE_BUCKET_NAME = config('SUPABASE_BUCKET_NAME', default='').strip()
SUPABASE_MEDIA_PREFIX = config('SUPABASE_MEDIA_PREFIX', default='').strip().strip('/')
SUPABASE_MEDIA_CACHE_CONTROL = config('SUPABASE_MEDIA_CACHE_CONTROL', default='3600')
SUPABASE_MEDIA_UPSERT = config('SUPABASE_MEDIA_UPSERT', default='true').strip().lower()
SUPABASE_BUCKET_PUBLIC = env_to_bool(config('SUPABASE_BUCKET_PUBLIC', default='True'), default=True)
SUPABASE_SIGNED_URL_EXPIRES = int(config('SUPABASE_SIGNED_URL_EXPIRES', default='3600'))

if USE_SUPABASE_STORAGE:
    missing_supabase_vars = [
        key for key, value in {
            'SUPABASE_URL': SUPABASE_URL,
            'SUPABASE_BUCKET_NAME': SUPABASE_BUCKET_NAME,
        }.items() if not value
    ]
    if not (SUPABASE_KEY or SUPABASE_SERVICE_ROLE_KEY):
        missing_supabase_vars.append('SUPABASE_KEY (yoki SUPABASE_SERVICE_ROLE_KEY)')

    if missing_supabase_vars:
        raise ValueError(
            "USE_SUPABASE_STORAGE=True bo'lsa quyidagi env lar majburiy: "
            + ", ".join(missing_supabase_vars)
        )

    STORAGES['default'] = {
        'BACKEND': 'core.storage_backends.SupabaseStorage',
    }

# Default primary key field type
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# DJANGO REST FRAMEWORK
# ============================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ============================================
# CORS SETTINGS
# ============================================

CORS_ALLOWED_ORIGINS = parse_origins(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:5173',
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGIN_REGEXES = [
    value.strip() for value in config('CORS_ALLOWED_ORIGIN_REGEXES', default='', cast=Csv()) if value.strip()
]
CSRF_TRUSTED_ORIGINS = parse_origins(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:3000,http://localhost:5173',
)

# Render/Vercel ajratilgan deploy uchun media serving (kichik loyiha uchun)
SERVE_MEDIA = env_to_bool(config('SERVE_MEDIA', default='True'), default=True)
DEBUG_PROPAGATE_EXCEPTIONS = env_to_bool(
    config('DEBUG_PROPAGATE_EXCEPTIONS', default='False'),
    default=False,
)

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'core.storage_backends': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# ============================================
# DJANGO UNFOLD ADMIN
# ============================================

UNFOLD = {
    "SITE_HEADER": "Adiblar Merosi",
    "SITE_TITLE": "Admin Panel",
    "SITE_SYMBOL": "menu_book",
    "SITE_URL": "/admin/",
    "ENVIRONMENT": "production" if not DEBUG else "development",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "DASHBOARD_CALLBACK": "core.unfold.dashboard_callback",
    "COLORS": {
        "primary": {
            "50": "#f3f4f6",
            "100": "#e5e7eb",
            "200": "#d1d5db",
            "300": "#9ca3af",
            "400": "#6b7280",
            "500": "#4b5563",
            "600": "#374151",
            "700": "#1f2937",
            "800": "#111827",
            "900": "#030712",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Tizim Boshqaruvi",
                "items": [
                    {
                        "title": "Foydalanuvchilar",
                        "icon": "people",
                        "link": "/admin/auth/user/",
                    },
                    {
                        "title": "Guruhlar",
                        "icon": "security",
                        "link": "/admin/auth/group/",
                    },
                ],
            },
            {
                "title": "Kontenti Boshqaruvi",
                "items": [
                    {
                        "title": "Yozuvchilar",
                        "icon": "person",
                        "link": "/admin/writers/writer/",
                    },
                    {
                        "title": "Asarlar",
                        "icon": "library_books",
                        "link": "/admin/works/literarywork/",
                    },
                    {
                        "title": "Kitob Fayllar",
                        "icon": "description",
                        "link": "/admin/works/bookfile/",
                    },
                ],
            },
            {
                "title": "Jamiyat",
                "items": [
                    {
                        "title": "Maqolalar",
                        "icon": "article",
                        "link": "/admin/articles/article/",
                    },
                    {
                        "title": "Sharhlar",
                        "icon": "comment",
                        "link": "/admin/articles/articlecomment/",
                    },
                ],
            },
        ],
    },
}

# ============================================
# JWT SETTINGS
# ============================================

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# ============================================
# EMAIL SETTINGS (Development)
# ============================================

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=1025, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@adiblarmerosi.com')

# ============================================
# AI CHAT SETTINGS (Optional)
# ============================================

OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
OPENAI_CHAT_MODEL = config('OPENAI_CHAT_MODEL', default='gpt-4.1-mini')

# ============================================
# REDIS CACHE (Optional)
# ============================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'adiblar-merosi',
    }
}

# Redis (uncomment if using Redis)
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }
