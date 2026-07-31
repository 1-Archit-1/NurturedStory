from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# DJANGO_ENV options: development | staging | production
# Defaults to development locally so nothing breaks without a .env file.
DJANGO_ENV = os.environ.get("DJANGO_ENV", "development")

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-dev-key-change-in-production")
DEBUG = DJANGO_ENV == "development"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
if DJANGO_ENV == "staging":
    ALLOWED_HOSTS += os.environ.get("STAGING_ALLOWED_HOSTS", "").split(",")
elif DJANGO_ENV == "production":
    ALLOWED_HOSTS += os.environ.get("PRODUCTION_ALLOWED_HOSTS", "").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "website",
]

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
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "website.context_processors.site_settings",
            ],
            "builtins": ["django.templatetags.static"],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

if DJANGO_ENV == "development":
    # Local dev: SQLite at the project root
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
elif DJANGO_ENV == "staging":
    DATABASES = {
        "default": dj_database_url.config(
            default=os.environ.get("STAGING_DATABASE_URL"),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
elif DJANGO_ENV == "production":
    # If a DATABASE_URL is set, use Postgres; otherwise fall back to SQLite
    # stored in /app/data/ which is mapped to a named Docker volume.
    _prod_db_url = os.environ.get("PRODUCTION_DATABASE_URL")
    if _prod_db_url:
        DATABASES = {
            "default": dj_database_url.config(
                default=_prod_db_url,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "data" / "db.sqlite3",
            }
        }
else:
    raise ValueError(f"Unknown DJANGO_ENV value: '{DJANGO_ENV}'. Must be development, staging, or production.")

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Uploaded files (e.g. therapist profile photo)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# EMAIL  (contact form notifications)
# =============================================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

# Address that receives contact form submissions
CONTACT_RECIPIENT_EMAIL = os.environ.get(
    "CONTACT_RECIPIENT_EMAIL", EMAIL_HOST_USER
)

# In development with no creds set, fall back to console so the site doesn't
# error out on form submission.
if not EMAIL_HOST_USER:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# =============================================================================
# PROXY / RATE LIMITING
# =============================================================================
# Trust the X-Forwarded-For header from Traefik (or Caddy) so django-ratelimit
# sees the real visitor IP rather than the proxy's internal IP.
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# =============================================================================
# CSRF TRUSTED ORIGINS
# =============================================================================
# Django requires the incoming Origin/Referer header to match one of these when
# submitting forms behind a proxy. Without this, contact form POSTs can 403
# in production even though the site loads fine.
CSRF_TRUSTED_ORIGINS: list[str] = []
if DJANGO_ENV == "staging":
    _staging_hosts = os.environ.get("STAGING_ALLOWED_HOSTS", "").split(",")
    CSRF_TRUSTED_ORIGINS = [f"https://{h.strip()}" for h in _staging_hosts if h.strip()]
elif DJANGO_ENV == "production":
    _prod_hosts = os.environ.get("PRODUCTION_ALLOWED_HOSTS", "").split(",")
    CSRF_TRUSTED_ORIGINS = [f"https://{h.strip()}" for h in _prod_hosts if h.strip()]

# =============================================================================
# SECURITY HEADERS  (production/staging only)
# =============================================================================
# Development runs on http://localhost so these would break dev if enabled.
if DJANGO_ENV in ("staging", "production"):
    # HTTPS redirect is handled by Cloudflare's "Always Use HTTPS" setting
    # at the edge, so we don't enforce it again at the Django level.
    # (Cloudflare SSL/TLS mode is "Full" — consider "Full (strict)" for
    # end-to-end cert verification against the origin's Let's Encrypt cert.)

    # Cookies only sent over HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS — tells browsers to only use HTTPS for this domain for 1 year
    # includeSubDomains covers www + apex
    # preload allows submission to the browser HSTS preload list (optional)
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Prevent the site being framed by other origins (clickjacking protection)
    X_FRAME_OPTIONS = "DENY"

    # Tell browsers not to guess/change the content-type of responses
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Send Referer only for same-origin requests (privacy)
    SECURE_REFERRER_POLICY = "same-origin"

# =============================================================================
# SITE URL  (used for canonical tags and Open Graph URLs)
# =============================================================================
# Set this to the full domain in production, e.g. https://nurturedstory.com
# Falls back to empty string in development (canonical tags still render, just
# without the domain prefix which is fine for local testing).
SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")
