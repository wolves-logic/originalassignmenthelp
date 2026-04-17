"""
settings.py
-----------
Django project settings for Original Assignment Help.

AWS integrations (all controlled by toggles in .env):
  USE_RDS=True   → Amazon RDS for PostgreSQL (production database)
  USE_S3=True    → Amazon S3 for media file storage
  USE_CACHE=True → Amazon ElastiCache for Redis (caching + sessions)

All credentials are read from .env via python-decouple.
NEVER hardcode secrets in this file.
"""

from pathlib import Path
from decouple import config, Csv

# ---------------------------------------------------------------------------
# Base directory
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Security settings — all read from .env, NEVER hardcoded
# ---------------------------------------------------------------------------
SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", default=False, cast=bool)

# Comma-separated list in .env, e.g. "127.0.0.1,localhost,yoursite.com"
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost",
    cast=Csv(),
)

# ---------------------------------------------------------------------------
# Production security hardening — only active when DEBUG=False
# ---------------------------------------------------------------------------
if not DEBUG:
    # ── SECURE_SSL_REDIRECT is intentionally disabled ─────────────────────
    # Django runs behind Nginx, which terminates SSL and forwards plain HTTP
    # to Gunicorn on port 8000.  SECURE_SSL_REDIRECT=True would see that
    # internal HTTP request and redirect to HTTPS, causing an infinite loop.
    #
    # HTTP→HTTPS enforcement is done at the Nginx layer:
    #   server { listen 80; return 301 https://$host$request_uri; }
    #
    # SECURE_PROXY_SSL_HEADER below tells Django to treat the connection as
    # HTTPS when Nginx sets 'X-Forwarded-Proto: https'.

    # Instruct browsers to always use HTTPS for 1 year (HSTS)
    SECURE_HSTS_SECONDS = 31_536_000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Only transmit session and CSRF cookies over encrypted connections
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Prevent MIME-type sniffing (defence-in-depth)
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Trust the X-Forwarded-Proto header set by Nginx.
    # Nginx config MUST include: proxy_set_header X-Forwarded-Proto https;
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "storages",           # django-storages (S3 backend)
    "django_ckeditor_5",
    # Local apps
    "Main",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "orignalassignmenthelp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "Main.processor.global_context",
            ],
        },
    },
]

WSGI_APPLICATION = "orignalassignmenthelp.wsgi.application"

# ---------------------------------------------------------------------------
# Database
#
# USE_RDS=True  → Amazon RDS for PostgreSQL (production)
# USE_RDS=False → SQLite on local disk (development / quick setup)
#
# RDS endpoint format:
#   your-instance-id.xxxxxxxxx.us-east-1.rds.amazonaws.com
# ---------------------------------------------------------------------------
USE_AWS_DB = config("USE_RDS", default=False, cast=bool)
USE_LOCAL_PG = config("USE_LOCAL_POSTGRES", default=True, cast=bool) # Use docker-compose postgres by default

if USE_AWS_DB:
    # -----------------------------------------------------------------------
    # Production AWS RDS
    # -----------------------------------------------------------------------
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("RDS_DB_NAME"),
            "USER": config("RDS_DB_USER"),
            "PASSWORD": config("RDS_DB_PASSWORD"),
            "HOST": config("RDS_DB_HOST"),
            "PORT": config("RDS_DB_PORT", default="5432"),
            "OPTIONS": {
                "sslmode": config("RDS_SSL_MODE", default="require"),
                "connect_timeout": 10,
            },
            "CONN_MAX_AGE": config("DB_CONN_MAX_AGE", default=60, cast=int),
            "CONN_HEALTH_CHECKS": True,
        }
    }
elif USE_LOCAL_PG:
    # -----------------------------------------------------------------------
    # Local Docker PostgreSQL
    # -----------------------------------------------------------------------
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("LOCAL_DB_NAME", default="oah_db"),
            "USER": config("LOCAL_DB_USER", default="oah_local"),
            "PASSWORD": config("LOCAL_DB_PASSWORD", default="oah_local_password"),
            "HOST": config("LOCAL_DB_HOST", default="127.0.0.1"),
            "PORT": config("LOCAL_DB_PORT", default="5432"),
            "CONN_MAX_AGE": 0,
        }
    }
else:
    # -----------------------------------------------------------------------
    # Local development fallback — SQLite
    # -----------------------------------------------------------------------
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static files (CSS, JS, fonts — NOT user uploads)
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Required for `collectstatic` in production.
STATIC_ROOT = BASE_DIR / "staticfiles"

# ---------------------------------------------------------------------------
# Media / File Storage
#
# USE_S3=True  → Amazon S3 via django-storages (production)
# USE_S3=False → Local filesystem under /media/ (development)
# ---------------------------------------------------------------------------
USE_S3 = config("USE_S3", default=False, cast=bool)

if USE_S3:
    # ------------------------------------------------------------------
    # AWS Credentials — read exclusively from .env
    # ------------------------------------------------------------------
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")

    # Use SigV4 signing (required for most regions outside us-east-1)
    AWS_S3_SIGNATURE_VERSION = "s3v4"

    # Do not silently overwrite existing files — append a unique suffix
    AWS_S3_FILE_OVERWRITE = False

    # Use the bucket-level ACL / Block Public Access settings instead
    # of per-object ACLs (modern AWS best practice)
    AWS_DEFAULT_ACL = None

    # Tell browsers to cache S3 files for 24 hours
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

    # Set to False for publicly accessible media (no expiring signed URLs).
    # Set to True if your bucket is private and you want signed URLs.
    AWS_QUERYSTRING_AUTH = False

    # Optional: CloudFront or custom domain.
    # Falls back to the standard S3 endpoint if not provided.
    _custom_domain = config("AWS_S3_CUSTOM_DOMAIN", default="")
    AWS_S3_CUSTOM_DOMAIN = (
        _custom_domain
        if _custom_domain
        else f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    )

    # MEDIA_URL points to the S3 bucket (under the 'media/' prefix
    # that MediaStorage sets as its `location`).
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

    # Override Django's default storage backends:
    #   default   → MediaStorage (uploads go to S3)
    #   staticfiles → kept as local/whitenoise for static files
    STORAGES = {
        "default": {
            "BACKEND": "Main.storage_backends.MediaStorage",
        },
        "staticfiles": {
            # Keep serving static files locally (or swap for
            # whitenoise / S3 later if desired)
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

else:
    # ------------------------------------------------------------------
    # Local filesystem storage (development / no AWS credentials)
    # ------------------------------------------------------------------
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Cache — Amazon ElastiCache for Redis (production) or LocMemCache (dev)
#
# USE_CACHE=True  → connects to ElastiCache via REDIS_URL (production)
# USE_CACHE=False → uses Django's built-in in-process cache (dev/testing)
#
# ElastiCache endpoint format (Redis):
#   Cluster mode OFF : redis://your-cluster.xxxxxx.ng.0001.use1.cache.amazonaws.com:6379
#   TLS enabled      : rediss://your-cluster.xxxxxx.ng.0001.use1.cache.amazonaws.com:6379
# ---------------------------------------------------------------------------
USE_CACHE = config("USE_CACHE", default=False, cast=bool)
REDIS_URL = config("REDIS_URL", default="redis://127.0.0.1:6379")

if USE_CACHE:
    CACHES = {
        "default": {
            # django-redis backend — works with local Redis AND ElastiCache
            "BACKEND": "django_redis.cache.RedisCache",

            # The REDIS_URL from .env — swap 127.0.0.1 for your ElastiCache
            # endpoint when deploying to production.
            "LOCATION": REDIS_URL,

            "OPTIONS": {
                # Use the standard django-redis client
                "CLIENT_CLASS": "django_redis.client.DefaultClient",

                # Connection pool: max 20 simultaneous Redis connections
                "CONNECTION_POOL_KWARGS": {"max_connections": 20},

                # Timeout settings — prevents hanging if Redis is slow
                "SOCKET_CONNECT_TIMEOUT": 5,   # seconds to establish connection
                "SOCKET_TIMEOUT": 5,            # seconds to wait for a response

                # CRITICAL for production resilience:
                # If Redis/ElastiCache goes down, cache operations return
                # None instead of raising an exception. The site gracefully
                # falls back to hitting the database rather than crashing.
                "IGNORE_EXCEPTIONS": True,

                # Compress large cache values to save ElastiCache memory
                "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            },

            # Prefix all cache keys with 'oah:' to namespace them within
            # the Redis instance (useful if multiple apps share one cluster)
            "KEY_PREFIX": "oah",

            # Default cache entry lifetime: 5 minutes.
            # Individual cache.set() calls can override this per-key.
            "TIMEOUT": 300,
        }
    }

    # Store Django sessions in Redis instead of the database.
    # This is faster (no DB query on every authenticated request) and
    # sessions expire automatically when the Redis TTL runs out.
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

else:
    # Development / CI: use Django's fast in-process memory cache.
    # No Redis installation required. Cache is cleared on server restart.
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "oah-local-cache",
        }
    }

# ---------------------------------------------------------------------------
# Default primary key field type
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Logging
# Errors are written to logs/django.log (rotating, max 10 MB × 5 files).
# In development (DEBUG=True) INFO+ also goes to the console.
# ---------------------------------------------------------------------------
_LOG_DIR = BASE_DIR / "logs"
_LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": _LOG_DIR / "django.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB per file
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO" if DEBUG else "WARNING",
            "propagate": False,
        },
        "Main": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}

# ---------------------------------------------------------------------------
# CKEditor 5 Settings
# ---------------------------------------------------------------------------

# Only staff users may upload files through the editor.
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "staff"

# Restrict to safe file types only — do NOT allow all file types.
CKEDITOR_5_ALLOW_ALL_FILE_TYPES = False
CKEDITOR_5_UPLOAD_FILE_TYPES = ["jpeg", "jpg", "png", "gif", "bmp", "webp"]

# Uploaded CKEditor images land in media/uploads/ (resolved by MediaStorage
# when USE_S3=True, or MEDIA_ROOT/uploads/ when local).
CKEDITOR_5_FILE_STORAGE_PATH = "uploads/"

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 300,
        "width": "100%",
    },
    "offer_config": {
        "toolbar": ["bold", "italic", "underline", "|", "link", "removeFormat"],
        "height": 100,
        "width": "100%",
    },
    "blog_config": {
        "toolbar": [
            "heading", "|",
            "fontSize", "fontFamily", "fontColor", "fontBackgroundColor", "|",
            "bold", "italic", "underline", "strikethrough", "subscript",
            "superscript", "removeFormat", "|",
            "alignment", "|",
            "bulletedList", "numberedList", "todoList", "|",
            "outdent", "indent", "|",
            "link", "insertImage", "blockQuote", "insertTable", "|",
            "undo", "redo",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "toggleImageCaption",
                "imageStyle:inline",
                "imageStyle:block",
                "imageStyle:side",
            ]
        },
        "table": {
            "contentToolbar": [
                "tableColumn", "tableRow", "mergeTableCells",
                "tableProperties", "tableCellProperties",
            ]
        },
        "height": 400,
        "width": "100%",
    },
}
