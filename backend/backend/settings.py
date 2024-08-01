import logging
from ast import literal_eval
import os
from pathlib import Path
from datetime import timedelta
import pymysql

logger= logging.getLogger(__name__)

print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")

pymysql.version_info = (1, 4, 13, "final", 0)  # 需自行新增
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

print(f"---------- Project DIR: {BASE_DIR}")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-h0usnb4^27w+^)i*)f24$i3$$)(&1m@r0cj42wsi1n@0&+7@h)"

SITE_ID = 1

# ----------------------------- START - DEBUG setting -------------------------------
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG')
if DEBUG is None:
    DEBUG = True
else:
    if isinstance(DEBUG, str):
        DEBUG = literal_eval(DEBUG)
    elif isinstance(DEBUG, bool):
        pass
print(f"---------- Debug mode: {DEBUG}")
# ------------------------------ END - DEBUG setting --------------------------------


ALLOWED_HOSTS = ["*"]

# -------------- START - CORS Setting --------------
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    "http://*.127.0.0.1",
    "http://localhost",
]
# -------------- END - CORS Setting -----------------

# -------------- START - Auth Setting --------------

SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"
# SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

LOGIN_REDIRECT_URL = "/"
VALID_REGISTER_DOMAINS = ["gmail.com", "hotmail.com"] # Only these domains can login.

# API URL Prefix
JWT_3RD_PREFIX = 'api'

# ================== Google Auth ==================
# Add this block if you want to login with Google.

SOCIAL_GOOGLE_CLIENT_ID = os.environ.get('SOCIAL_GOOGLE_CLIENT_ID')

# ================== END - Google Auth ==================

# --------------- END - Auth Setting -----------------

# Application definition

INSTALLED_APPS = [
    # admin skin
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    #"unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
    # websocket
    "daphne",
    "channels",
    "channels_redis",
    # django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # base
    "rest_framework",
    "drf_yasg",
    # package
    "bootstrap3",
    "djoser",
    "corsheaders",
    "simple_history",
    "author",
    "django_q",
    "django_simple_third_party_jwt", # https://github.com/NatLee/Django-Simple-3rd-Party-JWT
    "import_export",
    # custom
    "dev_dashboard",
    "custom_jwt",
    "api_proxy",
    "userprofile",
    # test
    "ping"
]

if DEBUG:
    INSTALLED_APPS += [
        "schema_graph", # Show visual schema graph
        "django_cprofile_middleware",
        "pyinstrument", # Show API performance
        "silk", # Show request performance
        "debug_toolbar", # SSR debug tool
    ]
    INTERNAL_IPS = [
        '127.0.0.1',
    ]

    # this is the main reason for not showing up the toolbar
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)

    def show_toolbar(request):
        return True

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK" : show_toolbar,
    }

UNFOLD = {
    "SITE_TITLE": "後端管理平台（Admin Platform）",
    "SITE_HEADER": "後端管理平台（Admin Platform）",
    # "THEME": "light", # Force theme: "dark" or "light". Will disable theme switcher
    "SIDEBAR": {
        "show_search": True,  # Search in applications and models names
        "show_all_applications": True,  # Dropdown with all applications and models
    }
}

ASGI_APPLICATION = "backend.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("backend-redis", 6379)],
        },
    },
}


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
    "author.middlewares.AuthorDefaultBackendMiddleware",
]

if DEBUG:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

    MIDDLEWARE += [
        "pyinstrument.middleware.ProfilerMiddleware",
        "silk.middleware.SilkyMiddleware",
        "django_cprofile_middleware.middleware.ProfilerMiddleware",
    ]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates").replace("\\", "/")],
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

# -------------- START - Swagger Setting --------------

USE_X_FORWARDED_HOST = True

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Token(add prefix `Bearer` yourself)": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        }
    },
    "LOGIN_URL": "/api/__hidden_dev_dashboard/login",
    "LOGOUT_URL": "/api/__hidden_admin/logout/?next=/api/__hidden_swagger",
}

# --------------- END - Swagger Setting----------------


# -------------- START - Database Setting --------------
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
#DB_USER_PASSWORD = os.environ["DB_USER_PASSWORD"] # for security reasons
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
SQL = {
    "ENGINE": "django.db.backends.mysql",
    "NAME": DB_NAME,  # db name
    "USER": DB_USER,  # db user
    "PASSWORD": os.environ["DB_USER_PASSWORD"],  # db password
    "HOST": DB_HOST,  # db host
    "PORT": DB_PORT,  # db port
}
DATABASES = {"default": SQL, "OPTIONS": {"protocol": "TCP"}}
print(f"---------- MYSQL: {DB_NAME} -> {DB_USER}@{DB_HOST}:{DB_PORT}")
# -------------- END - Database Setting --------------



# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

from django.conf.locale.en import formats as en_formats
en_formats.DATETIME_FORMAT = "Y/m/d H:i:s"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Taipei"
USE_I18N = True
USE_L10N = True
USE_TZ = True
APPEND_SLASH = False

# Static files (CSS, JavaScript, Images)
STATIC_URL = "api/__hidden_statics/"
STATIC_ROOT = "staticfiles"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------- START - Log setting --------------
LOG_ROOT = Path(BASE_DIR) / 'logs'
LOG_ROOT.mkdir(exist_ok=True)

LOG_TYPES = {
    'file': 'standard',
    'database': 'standard',
    'api': 'api-format',
    'auth': 'standard',
}

FORMATTERS = {
    'standard': {
        'format': '[%(asctime)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s] - %(message)s'
    },
    "simple": {
        "format": "%(levelname)s %(message)s"
    },
    "api-format": {
        "format": "[%(asctime)s] [%(funcName)s:%(lineno)d] [%(levelname)s] - %(message)s"
    },
}

for log_type in LOG_TYPES.keys():
    log_type_path = Path(BASE_DIR) / 'logs' / log_type
    log_type_path.mkdir(exist_ok=True)

HANDLERS = {}

for log_type, formatter in LOG_TYPES.items():
    HANDLERS[log_type] = {
        'class': 'common.log.InterceptTimedRotatingFileHandler',
        'filename': f"{LOG_ROOT / log_type / f'{log_type}.log'}",
        'when': "H",
        'interval': 1,
        'backupCount': 1,
        'formatter': formatter,
        'encoding': 'utf-8',
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': FORMATTERS,
    'filters': {
    },
    'handlers': HANDLERS,
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': "INFO"
        },
        'django.request': {
            'handlers': ['file'],
            'propagate': False,
            'level': "DEBUG"
        },
        "custom_auth": {
            "handlers": ["auth"],
            "propagate": False,
            "level": "DEBUG"
        },
        # JWT相關
        "custom_jwt": {
            "handlers": ["auth"],
            "propagate": False,
            "level": "DEBUG"
        },
    }
}


# --------------- END - Log setting ---------------


# ---------------------------- START - REST_FRAMEWORK setting --------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # 支援使用simplejwt的JWT登入
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # 支援一般session進行後台登入
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": (
        # restframework的API必須登入才可使用
        "rest_framework.permissions.IsAuthenticated",
    ),
    # 使用JSON來render API而非HTML界面
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}
# ----------------------------- END - REST_FRAMEWORK setting ----------------------------



# -------------- Start - SimpleJWT Setting --------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=3600),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}
# -------------- END - SimpleJWT Setting --------------


# -------------- START - APIProxy Setting --------------
API_URL = os.environ.get("API_URL")
API_VERSION = os.environ.get("API_VERSION")
ROUTE_PATH='proxy' # default route
TARGET_PATH='api' # target route path
print(f"---------- API Proxy: {TARGET_PATH} -> {ROUTE_PATH}")
# -------------- END - APIProxy Setting --------------


# -------------- START - Redis Setting --------------
REDIS_PORT = 6379
REDIS_HOST = "redis://backend-redis"
CACHES = { # Redis cache
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_HOST}:{REDIS_PORT}/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
print(f"---------- REDIS: {REDIS_HOST}:{REDIS_PORT}")

# -------------- END - Redis Setting --------------

# -------------- Start - Django Q --------------
Q_CLUSTER = {
    'name': 'backend',
    'workers': 3,
    'recycle': 500,
    'retry': 3700,
    'timeout': 3600,
    'compress': True,
    'save_limit': 250,
    'queue_limit': 250,
    # 'cpu_affinity': 1,
    'label': 'Django Q',
    'orm': 'default',
    'max_attempts': 2
}
# -------------- END - Django Q --------------



# -------------- START - Cache Page Setting --------------
CACHE_PAGE = False
CACHE_TTL = 60 * 60
print(f"---------- CACHE PAGE: {CACHE_PAGE}")
print(f"---------- CACHE TTL: {CACHE_TTL} sec(s)")
# -------------- END - Cache Page Setting --------------

print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")
