"""
Django settings for artisan marketplace project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
# ------------------------------------------------------------------------------
# BASE DIRECTORY & ENVIRONMENT
# ------------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Frontend URL (for redirect after payment verification)
FRONTEND_URL = 'http://localhost:5173'   # or your production frontend URL

# Backend URL (for Paystack callback)
BACKEND_URL = 'http://127.0.0.1:8000'   # adjust for production

# ------------------------------------------------------------------------------
# SECURITY
# ------------------------------------------------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-sk-@pvc3q+mal_1gs&015uz1d!r0zesqh4bt+-l8j9+!-pwkla")
DEBUG = os.getenv("DEBUG", "True") == "True"

# ========== FIX: ALLOWED_HOSTS ==========
# In development, always allow localhost and 127.0.0.1
# In production, read from .env
if DEBUG:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '::1'] + os.getenv("ALLOWED_HOSTS", "").split(",")
else:
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
# Remove empty entries
ALLOWED_HOSTS = ["backendapi-tv2v.onrender.com","127.0.0.1", "localhost"]
# =========================================



load_dotenv()



# ─── Email Configuration (SendGrid) ───────────────────────────────
# ==============================================================================
# EMAIL CONFIGURATION (SendGrid)
# ==============================================================================

# ─── Email Configuration (SendGrid Web API) ────────────────────
import os

# ─── Email Configuration (Gmail SMTP) ────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('GMAIL_EMAIL')
EMAIL_HOST_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('GMAIL_EMAIL')
# ------------------------------------------------------------------------------
# APPLICATIONS
# ------------------------------------------------------------------------------

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "channels",  # ✅ Already present

    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "drf_yasg",
    'model_utils',

    # Your local apps
    "accounts",
    "customers",
    "profiles",
    "artisans",
    "clients",
    "companies",
    "categories",
    "services",
    'call_center',
    'audit',
    "payments",
    "wallets",
    "subscriptions",
    "invoices",
    'dashboard',
    
    
    "notifications",
    "support",
    
   
    "ai",
    
    "billing",
        
    "learning",
    "recruitment",
    "organizations",
    'analytics',
    'sla',
    "reports",
    
    "permissions",
    "verification",
    "media",
    "app_settings",
    "common",
    "core",
    
    "incident_priority",
    "incident_category",
    'incident_statuses',
    'incidents',
    'attachments',
    'comments', 
    'assignments',
]

# ------------------------------------------------------------------------------
# CUSTOM USER MODEL
# ------------------------------------------------------------------------------

AUTH_USER_MODEL = "accounts.User"

# ------------------------------------------------------------------------------
# MIDDLEWARE (CorsMiddleware must be near the top)
# ------------------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------------------------------------------------------------------------
# URLS
# ------------------------------------------------------------------------------

ROOT_URLCONF = "config.urls"

# ------------------------------------------------------------------------------
# TEMPLATES
# ------------------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ------------------------------------------------------------------------------
# WSGI & ASGI
# ------------------------------------------------------------------------------

WSGI_APPLICATION = "config.wsgi.application"

# ─── NEW: ASGI for Channels (WebSockets) ────────────────────
ASGI_APPLICATION = "config.asgi.application"

# ─── NEW: Channel Layers (Redis) ─────────────────────────────
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# ------------------------------------------------------------------------------
# DATABASE (SQLite by default)
# ------------------------------------------------------------------------------

DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600,
        ssl_require=True,
    )
}

# ------------------------------------------------------------------------------
# PASSWORD VALIDATION
# ------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------------------------
# AUTHENTICATION BACKENDS
# ------------------------------------------------------------------------------

AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ------------------------------------------------------------------------------
# INTERNATIONALIZATION
# ------------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Accra"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# STATIC & MEDIA FILES
# ------------------------------------------------------------------------------

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ─── Storage backends ──────────────────────────────────────
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ------------------------------------------------------------------------------
# DEFAULT PRIMARY KEY
# ------------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------------------------
# LOGIN / LOGOUT REDIRECTS
# ------------------------------------------------------------------------------

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/login/"

# ------------------------------------------------------------------------------
# CORS (development / production)
# ------------------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = [
    "https://frontendapi-q90c.onrender.com",
    "http://localhost:5173",
]

CORS_ALLOW_CREDENTIALS = True

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

# ------------------------------------------------------------------------------
# REST FRAMEWORK
# ------------------------------------------------------------------------------

REST_FRAMEWORK = {
    
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "user": "1000/day",
        "anon": "100/day",
    },
}

# ------------------------------------------------------------------------------
# SIMPLE JWT
# ------------------------------------------------------------------------------

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# ------------------------------------------------------------------------------
# SECURITY HEADERS
# ------------------------------------------------------------------------------

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ------------------------------------------------------------------------------
# EMAIL
# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------
# PAYSTACK
# ------------------------------------------------------------------------------

PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY", "")
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "")
PAYSTACK_CALLBACK_URL = os.getenv("PAYSTACK_CALLBACK_URL", "http://127.0.0.1:8000/api/payments/verify/")

# ------------------------------------------------------------------------------
# CELERY
# ------------------------------------------------------------------------------

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# ------------------------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# ─── FORCE SENDGRID SETTINGS ─────────────────────────────────────



JAZZMIN_SETTINGS = {
    "site_title": "Artisan Call Center",
    "site_header": "Artisan Management",
    "site_brand": "Artisan CMS",
    "welcome_sign": "Welcome to Artisan Call Center",
    "copyright": "Shaz Data Consult",
    "site_logo": "images/logo.png",
    "login_logo": "images/logo.png",
    
    "site_logo_classes": "img-circle",

    "show_sidebar": True,
    "navigation_expanded": True,
    "show_ui_builder": True,

    "icons": {
        "accounts.User": "fas fa-users",
        "artisans.ArtisanProfile": "fas fa-tools",
        "wallets.Wallet": "fas fa-wallet",
        "incidents.Incident": "fas fa-exclamation-circle",
        "calls.Call": "fas fa-phone",
        "bookings.Booking": "fas fa-calendar",
        "payments.Payment": "fas fa-credit-card",
    },

    "hide_apps": [],
    "hide_models": [],
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
}