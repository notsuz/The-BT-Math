"""
Base Django settings shared by all environments.
Environment-specific overrides live in dev.py / prod.py.
"""

from datetime import timedelta
from pathlib import Path

import environ

# BASE_DIR points to the project root (two levels up from this file:
# config/settings/base.py -> config/ -> project root).
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-change-me-in-env")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

SITE_NAME = env("SITE_NAME", default="The BT Math")
SITE_URL = env("SITE_URL", default="http://127.0.0.1:8000")

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
]

LOCAL_APPS = [
    "apps.users",
    "apps.catalog",
    "apps.orders",
    "apps.payments",
    "apps.pages",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.catalog.context_processors.navigation",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database (PostgreSQL, configured entirely from the environment)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Custom user model
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "orders:my_courses"
LOGOUT_REDIRECT_URL = "pages:home"

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kathmandu"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# django-jazzmin's admin/base.html does `{% static 'vendor/bootswatch' %}` on
# a bare directory (used as a JS-side base path for theme switching, not a
# real file), which trips the manifest storage's strict mode with
# "Missing staticfiles manifest entry for 'vendor/bootswatch'" -> 500 on
# every admin page. Falling back to the unhashed URL for unknown entries
# fixes it without giving up cache-busting for everything else.
WHITENOISE_MANIFEST_STRICT = False

# Publicly served media (thumbnails, free-preview files).
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Locked content (paid PDFs etc.) lives OUTSIDE of MEDIA_ROOT/anything wired
# to a public URL. It is only ever read from disk by
# apps.catalog.views.ProtectedContentView after a purchase/free check, so
# there is no direct URL that serves it. See requirement #11 (secure files).
PRIVATE_MEDIA_ROOT = BASE_DIR / "private_media"

# ---------------------------------------------------------------------------
# Email (used for password reset)
# ---------------------------------------------------------------------------
EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@thebtmath.local")

# ---------------------------------------------------------------------------
# Django REST Framework / JWT / drf-spectacular
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "The BT Math API",
    "DESCRIPTION": "API for The BT Math e-learning platform (courses, orders, payments).",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ---------------------------------------------------------------------------
# Payment gateways (sandbox/test mode)
# ---------------------------------------------------------------------------
ESEWA_MERCHANT_CODE = env("ESEWA_MERCHANT_CODE", default="EPAYTEST")
ESEWA_SECRET_KEY = env("ESEWA_SECRET_KEY", default="8gBm/:&EnhH.1/q")
ESEWA_PAYMENT_URL = env(
    "ESEWA_PAYMENT_URL", default="https://rc-epay.esewa.com.np/api/epay/main/v2/form"
)
ESEWA_STATUS_CHECK_URL = env(
    "ESEWA_STATUS_CHECK_URL",
    default="https://rc.esewa.com.np/api/epay/transaction/status/",
)

KHALTI_SECRET_KEY = env("KHALTI_SECRET_KEY", default="")
KHALTI_INITIATE_URL = env(
    "KHALTI_INITIATE_URL",
    default="https://dev.khalti.com/api/v2/epayment/initiate/",
)
KHALTI_LOOKUP_URL = env(
    "KHALTI_LOOKUP_URL", default="https://dev.khalti.com/api/v2/epayment/lookup/"
)

PAYMENT_SUCCESS_URL_NAME = "orders:payment_success"
PAYMENT_FAILURE_URL_NAME = "orders:payment_failure"

# ---------------------------------------------------------------------------
# Admin theme (django-jazzmin)
# ---------------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": f"{SITE_NAME} Admin",
    "site_header": SITE_NAME,
    "site_brand": SITE_NAME,
    "site_logo": None,
    "login_logo": None,
    "site_icon": None,
    "welcome_sign": f"Welcome to the {SITE_NAME} admin panel",
    "copyright": SITE_NAME,
    # Jazzmin renders one navbar search bar per entry here, so listing
    # several models produces several separate top-bar search boxes. Each
    # changelist page already has its own search box + filters + Search
    # button (see admin-custom.css), so skip the navbar ones entirely and
    # keep a single search bar per page.
    "search_model": None,
    "user_avatar": None,
    "topmenu_links": [
        {"name": "View Site", "url": "pages:home", "new_window": True},
        {"model": "users.User"},
        {"app": "catalog"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["users", "catalog", "orders", "payments", "pages", "auth"],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.Group": "fas fa-users",
        "users.User": "fas fa-user-graduate",
        "catalog.Category": "fas fa-layer-group",
        "catalog.Program": "fas fa-graduation-cap",
        "catalog.Course": "fas fa-book",
        "catalog.Chapter": "fas fa-bookmark",
        "catalog.ContentItem": "fas fa-file-alt",
        "orders.Order": "fas fa-shopping-cart",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "custom_css": "css/admin-custom.css",
    "custom_js": None,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "default_theme_mode": "dark",
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "flatly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
# Django's own default LOGGING config only sends request errors to the
# console when DEBUG=True, so on a production host (DEBUG=False) a 500 error
# leaves no trace anywhere you can see it. Send them to stderr unconditionally
# so they show up in Render's/PythonAnywhere's log viewers.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

# ---------------------------------------------------------------------------
# Security defaults (tightened further in prod.py)
# ---------------------------------------------------------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
