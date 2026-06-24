"""Django development settings."""

from .base import *

DEBUG = False
ALLOWED_HOSTS = ["*"]

# Override for development
DATABASES["default"]["HOST"] = os.getenv("DB_HOST")
DATABASES["default"]["PORT"] = os.getenv("DB_PORT")
