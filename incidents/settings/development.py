"""Django development settings."""

import os

from .base import *

DEBUG = False
ALLOWED_HOSTS = ["*"]

# Override for development
DATABASES["default"]["HOST"] = os.getenv("DB_HOST")  # noqa: F405
DATABASES["default"]["PORT"] = os.getenv("DB_PORT")  # noqa: F405
