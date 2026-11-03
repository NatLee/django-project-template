"""Django settings for the template.

Everything that changes between projects or environments is read from environment
variables (Docker Compose loads them from `.env`). Defaults are safe for production:
with DEBUG off you must provide SECRET_KEY and ALLOWED_HOSTS yourself.
"""

from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from backend.env import env_bool, env_int, env_list, env_str

BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_NAME = env_str("PROJECT_NAME", "django-project-template")
DEBUG = env_bool("DEBUG", False)

# ------------------------------------------------------------------ security
SECRET_KEY = env_str("SECRET_KEY")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured(
            "SECRET_KEY is required when DEBUG is off. Generate one with: "
            "python -c \"import secrets; print(secrets.token_urlsafe(50))\""
        )
    # Only ever used in development; `manage.py check --deploy` flags it.
    SECRET_KEY = "django-insecure-development-only-key-do-not-use-in-production"

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "*" if DEBUG else "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

# NGINX in front of Django sets X-Forwarded-Proto and the original Host header.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Cookies only travel over HTTPS in production. Turn SECURE_COOKIES off if you
# run DEBUG=False on plain HTTP (for example a quick local check).
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = env_bool("SECURE_COOKIES", not DEBUG)
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)
SECURE_HSTS_SECONDS = env_int("SECURE_HSTS_SECONDS", 0)
SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"
# The social login runs in a popup window, so keep the opener relationship.
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS", DEBUG)
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True

# ------------------------------------------------------------------ apps
INSTALLED_APPS = [
    # Websocket (daphne must come first so `runserver` speaks ASGI)
    "daphne",
    "channels",
    # Django
    "django.contrib.sites",  # allauth needs SITE_ID
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",  # API framework
    "drf_yasg",  # Swagger / Redoc
    "corsheaders",  # CORS
    "simple_history",  # model change history
    "django_q",  # background tasks (django-q2)
    "import_export",  # import / export in the admin
    # Social login
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.microsoft",
    # Project apps
    "authentication",  # social login adapter that hands out JWTs
    "custom_jwt",  # JWT endpoints
    "dev_dashboard",  # login playground (DEBUG only)
    "api_proxy",  # forwards requests to another API
    "django_login_history",  # who logged in, when and from where
    "userprofile",  # extra fields for every user
    "ping",  # websocket + background task examples (DEBUG only)
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# Debug tools are only installed when DEBUG is on. urls.py mounts each tool's
# pages only when its app is installed.
if DEBUG:
    INSTALLED_APPS += [
        "schema_graph",  # visual model graph
        "django_cprofile_middleware",
        "pyinstrument",  # add ?profile to a URL
        "silk",  # request inspector
        "debug_toolbar",
    ]
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        *MIDDLEWARE,
        "pyinstrument.middleware.ProfilerMiddleware",
        "silk.middleware.SilkyMiddleware",
        "django_cprofile_middleware.middleware.ProfilerMiddleware",
    ]
    INTERNAL_IPS = ["127.0.0.1"]

    def show_toolbar(request):
        # Requests arrive through NGINX, so REMOTE_ADDR is never in INTERNAL_IPS.
        return True

    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": show_toolbar, "SHOW_COLLAPSED": True}

ROOT_URLCONF = "backend.urls"
ASGI_APPLICATION = "backend.asgi.application"

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
                "backend.context_processors.project",
            ],
        },
    },
]

# ------------------------------------------------------------------ database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env_str("DB_NAME", required=True),
        "USER": env_str("DB_USER", required=True),
        "PASSWORD": env_str("DB_USER_PASSWORD", required=True),
        "HOST": env_str("DB_HOST", "backend-postgres"),
        "PORT": env_int("DB_PORT", 5432),
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------------ redis: cache + websocket layer
REDIS_URL = env_str("REDIS_URL", "redis://backend-redis:6379/0")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    }
}

# Page cache used by common.cache_deco.CacheDeco
CACHE_PAGE = env_bool("CACHE_PAGE", False)
CACHE_TTL = env_int("CACHE_TTL", 60 * 60)

# ------------------------------------------------------------------ background tasks (django-q2)
Q_CLUSTER = {
    "name": "backend",
    "workers": env_int("Q_WORKERS", 3),
    "recycle": 500,
    "retry": 3700,  # must be longer than timeout
    "timeout": 3600,
    "compress": True,
    "save_limit": 250,
    "queue_limit": 250,
    "label": "Django Q",
    "orm": "default",  # the database is the broker, no extra service needed
    "max_attempts": 2,
}

# ------------------------------------------------------------------ auth
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_REDIRECT_URL = "/"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env_int("JWT_ACCESS_TOKEN_MINUTES", 3600)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env_int("JWT_REFRESH_TOKEN_DAYS", 1)),
}

# ------------------------------------------------------------------ social login (django-allauth)
# A provider is switched on by setting SOCIAL_<PROVIDER>_CLIENT_ID in .env.
# Add a provider: add its allauth app to INSTALLED_APPS and a line here.
SOCIAL_PROVIDER_SETTINGS = {
    "google": {},
    "microsoft": {"tenant": env_str("SOCIAL_MICROSOFT_TENANT", "common")},
}
SOCIALACCOUNT_PROVIDERS = {
    provider: {
        "APPS": [
            {
                "client_id": env_str(f"SOCIAL_{provider.upper()}_CLIENT_ID"),
                "secret": env_str(f"SOCIAL_{provider.upper()}_CLIENT_SECRET"),
                "settings": extra,
            }
        ]
    }
    for provider, extra in SOCIAL_PROVIDER_SETTINGS.items()
    if env_str(f"SOCIAL_{provider.upper()}_CLIENT_ID")
}
# Only emails from these domains may sign up or connect. Empty means any domain.
SOCIALACCOUNT_VALID_EMAIL_DOMAINS = env_list("SOCIALACCOUNT_VALID_EMAIL_DOMAINS", "gmail.com,hotmail.com")

SOCIALACCOUNT_LOGIN_ON_GET = True  # the dashboard links straight to the provider
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGIN_METHODS = {"username"}  # same as the JWT and playground logins
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]  # social sign-ups fill these in automatically
ACCOUNT_ADAPTER = "authentication.adapter.MyAccountAdapter"
SOCIALACCOUNT_ADAPTER = "authentication.adapter.MySocialAccountAdapter"

# ------------------------------------------------------------------ API docs (drf-yasg)
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Token(add prefix `Bearer` yourself)": {"type": "apiKey", "name": "Authorization", "in": "header"},
    },
    "LOGIN_URL": "/api/__hidden_dev_dashboard/login",
    "LOGOUT_URL": "/api/__hidden_admin/logout/?next=/api/__hidden_swagger",
}
SWAGGER_USE_COMPAT_RENDERERS = False  # formats are "json"/"yaml" without the dot (see urls.py)

# ------------------------------------------------------------------ API proxy
API_URL = env_str("API_URL")  # e.g. http://my-other-service:9999/
API_VERSION = env_str("API_VERSION", "v1")  # sent as the `version` header
ROUTE_PATH = "proxy"  # /api/proxy/<resource> ...
TARGET_PATH = "api"  # ... is forwarded to {API_URL}api/<resource>
API_PROXY_TIMEOUT = env_int("API_PROXY_TIMEOUT", 180)
API_PROXY_VERIFY_TLS = env_bool("API_PROXY_VERIFY_TLS", True)

# ------------------------------------------------------------------ login history
# "{ip}" is replaced by the address. Leave empty to skip the location lookup.
LOGIN_HISTORY_GEOIP_URL = env_str("LOGIN_HISTORY_GEOIP_URL", "http://ip-api.com/json/{ip}")
LOGIN_HISTORY_GEOIP_TIMEOUT = 5
LOGIN_HISTORY_RETENTION_DAYS = env_int("LOGIN_HISTORY_RETENTION_DAYS", 90)

# ------------------------------------------------------------------ i18n
LANGUAGE_CODE = env_str("LANGUAGE_CODE", "en-us")
TIME_ZONE = env_str("TIME_ZONE", "Asia/Taipei")
USE_I18N = True
USE_TZ = True
FORMAT_MODULE_PATH = ["backend.formats"]  # 2026/11/04 13:45:00 style dates
APPEND_SLASH = False

# ------------------------------------------------------------------ static files
STATIC_URL = "api/__hidden_statics/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# ------------------------------------------------------------------ logging
# Each category below gets its own folder under LOG_DIR with hourly rotated files,
# one file per level. loguru also prints these records to the console, so they
# show up in `docker compose logs`. Everything else goes to the console at WARNING.
LOG_DIR = Path(env_str("LOG_DIR", str(BASE_DIR / "logs")))
# Level for the project's own loggers; Django itself logs at INFO.
LOG_LEVEL = env_str("LOG_LEVEL", "DEBUG" if DEBUG else "INFO")
LOG_CATEGORIES = {
    # category: (formatter, level, loggers that write to it)
    "file": ("standard", "INFO", ["django"]),
    "database": ("standard", "INFO", ["django.db.backends"]),  # DEBUG here logs every SQL query
    "api": ("api-format", LOG_LEVEL, ["api_proxy"]),
    "auth": ("standard", LOG_LEVEL, ["authentication", "custom_jwt", "django_login_history"]),
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s] - %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},
        "api-format": {"format": "[%(asctime)s] [%(funcName)s:%(lineno)d] [%(levelname)s] - %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "standard"},
        **{
            category: {
                "class": "common.log.InterceptTimedRotatingFileHandler",
                "filename": str(LOG_DIR / category / f"{category}.log"),
                "when": "H",
                "interval": 1,
                "backupCount": 1,
                "formatter": formatter,
                "encoding": "utf-8",
            }
            for category, (formatter, _, _) in LOG_CATEGORIES.items()
        },
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        name: {"handlers": [category], "level": level, "propagate": False}
        for category, (_, level, names) in LOG_CATEGORIES.items()
        for name in names
    },
}
