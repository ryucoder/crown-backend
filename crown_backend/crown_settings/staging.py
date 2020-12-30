import os

from crown_backend.crown_settings.base import *

import environ

environ.Env.read_env("env/staging")
env = environ.Env()


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS += [
    "django_extensions",
    "debug_toolbar",
]

# For Django Debug Toolbar
INTERNAL_IPS = [
    "127.0.0.1",
]


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "packfect-staging.sqlite3"),
    }
}
