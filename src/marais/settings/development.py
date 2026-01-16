from .base import *
import os

DEBUG = True

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key')

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0')

# Use SQLite locally unless explicitly requested to use Postgres
if os.getenv('DEV_USE_POSTGRES', '').lower() != 'true':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Make local origins trusted for dev
CSRF_TRUSTED_ORIGINS = CSRF_TRUSTED_ORIGINS + [
    'http://localhost',
    'http://127.0.0.1:8000',
    'http://localhost:8585',
]
CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS + [
    'http://localhost',
    'http://127.0.0.1:8000',
    'http://localhost:8585',
]

# Relaxed security for development
SECURE_SSL_REDIRECT = False

# Emails to console in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
