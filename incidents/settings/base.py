"""Django base settings - Shared configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR / "incidents"

ALLOWED_HOSTS = ["*"]

# SECURITY WARNING: keep the secret key used in production secret!
# In production, load from environment variable
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "change-this-in-production-load-from-env-variable",
)

# Application definition
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "drf_spectacular",
    "corsheaders",
    "incidents.infrastructure.config.django_setup.IncidentsConfig",
    "django_prometheus",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "incidents.infrastructure.api.middleware.error_handler.ErrorHandlerMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost").split(",")

CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")

ROOT_URLCONF = "incidents.urls"
WSGI_APPLICATION = "incidents.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]

load_dotenv()

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

# JWT ConfigurationF
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "RS256")
JWT_PUBLIC_KEY_PATH = os.getenv("JWT_PUBLIC_KEY_PATH")

JWT_PUBLIC_KEY = ""

if JWT_PUBLIC_KEY_PATH and Path(JWT_PUBLIC_KEY_PATH).exists():
    with open(JWT_PUBLIC_KEY_PATH, "r", encoding="utf-8") as key_file:
        JWT_PUBLIC_KEY = key_file.read()

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "incidents.infrastructure.api.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "FleetOps Incidents Service API",
    "DESCRIPTION": "Documentación OpenAPI del servicio de incidentes de FleetOps.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "COMPONENT_SPLIT_REQUEST": True,
    "SERVERS": [
        {
            "url": os.getenv("SWAGGER_SERVER_URL", "http://100.31.63.184:8080"),
            "description": "FleetOps Incidents API",
        }
    ],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
    "SECURITY": [{"bearerAuth": []}],
}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# Internationalization
LANGUAGE_CODE = "es-CO"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Environment flag used by infrastructure bootstrap code.
TESTING = False
