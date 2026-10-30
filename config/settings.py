
"""
Django settings for Royalty Events — Event & Venue Management System.
Django 5.2 / Python 3.14
"""

import os
from pathlib import Path

# ── Base directory ──────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── Environment variables ───────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

# ── Security ────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "fallback-insecure-key-only-for-ci-replace-in-production",
)

DEBUG = os.environ.get("DEBUG", "True").lower() in (
    "1", "true", "yes"
)

if not DEBUG and SECRET_KEY == "fallback-insecure-key-only-for-ci-replace-in-production":
    raise ValueError(
        "Production SECRET_KEY environment variable is required."
    )

_allowed = os.environ.get(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1",
)

ALLOWED_HOSTS = [
    host.strip()
    for host in _allowed.split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS", ""
    ).split(",")
    if origin.strip()
]

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

# ── Application ─────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "events",
]

# ── Middleware ───────────────────────────────────────────────
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

# ── Templates ───────────────────────────────────────────────
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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ── Database ────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ── Password validation ──────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 6},
    },
]

# ── Internationalisation ─────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# ── Static files ────────────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "events" / "static"
]
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# ── Media files ─────────────────────────────────────────────
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── Authentication ──────────────────────────────────────────
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# ── Email ────────────────────────────────────────────────────
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)

EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))

EMAIL_USE_TLS = os.environ.get(
    "EMAIL_USE_TLS", "True"
).lower() in ("1", "true", "yes")

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "Royalty Events <noreply@royaltyevents.com>",
)

STAFF_NOTIFICATION_EMAIL = os.environ.get(
    "STAFF_NOTIFICATION_EMAIL",
    "staff@royaltyevents.com",
)

# ── Production security ─────────────────────────────────────
if not DEBUG:
    SECURE_HSTS_SECONDS = 3600
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

# ── Default primary key ─────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Upload limits ───────────────────────────────────────────
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
