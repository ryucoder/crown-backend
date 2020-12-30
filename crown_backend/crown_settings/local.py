import os

from crown_backend.crown_settings.base import *

import environ

environ.Env.read_env("env/local")
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


MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "crown-local.sqlite3"),
    }
}
