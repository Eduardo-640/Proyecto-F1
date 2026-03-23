import os
from .base import *  # noqa
import dj_database_url

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': dj_database_url.config(
        env='DATABASE_URL',
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=0,
    )
}

_cors_origins_raw = os.getenv('CORS_ALLOWED_ORIGINS', '').strip()
if _cors_origins_raw:
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in _cors_origins_raw.split(',') if origin]
else:
    CORS_ALLOWED_ORIGINS = ['http://localhost:5173']

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
