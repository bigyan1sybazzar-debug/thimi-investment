"""
Django settings for backend project.
"""

import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-+ke3&9yio8e!t_&!t73s5-j&ru-ip_&#^wmcy#^k!aoe9j7k9^'
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS_ENV = os.environ.get('ALLOWED_HOSTS', '')
if ALLOWED_HOSTS_ENV:
    # Strip any http://, https://, whitespace or trailing slashes that cause 400 Bad Request
    parsed_hosts = []
    for h in ALLOWED_HOSTS_ENV.split(','):
        clean_h = h.strip().replace('https://', '').replace('http://', '').split('/')[0].split(':')[0]
        if clean_h:
            parsed_hosts.append(clean_h)
    # Ensure default domains and localhost are always allowed
    for default_h in ['localhost', '127.0.0.1', 'thimiinvestment.com', 'www.thimiinvestment.com', '.thimiinvestment.com', '.up.railway.app']:
        if default_h not in parsed_hosts:
            parsed_hosts.append(default_h)
    ALLOWED_HOSTS = parsed_hosts
else:
    ALLOWED_HOSTS = ['*']

# Reverse proxy / CGI headers support
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',

    'accounts',
    'members',
    'deposits',
    'investments',
    'loans',
    'notifications_app',
    'webui',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Database — uses DATABASE_URL on Railway, falls back to SQLite locally
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
}


CORS_ALLOW_ALL_ORIGINS = True
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CSRF trusted origins — add your Railway/production domain(s) here
CSRF_TRUSTED_ORIGINS_ENV = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [
    'https://thimi-investment-aa.up.railway.app',
    'https://www.thimiinvestment.com',
    'https://thimiinvestment.com',
    'http://www.thimiinvestment.com',
    'http://thimiinvestment.com',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://127.0.0.1',
    'http://localhost',
] + [o.strip() for o in CSRF_TRUSTED_ORIGINS_ENV.split(',') if o.strip()]

# Email Settings (cPanel Domain Email - SMTP SSL)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'mail.thimiinvestment.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 465))
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'admin@thimiinvestment.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'Qwater123@')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Thimi Investment Group <admin@thimiinvestment.com>')
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', 30))

# Google OAuth Credentials
try:
    from decouple import config
    GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default=os.environ.get('GOOGLE_CLIENT_ID', ''))
    GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default=os.environ.get('GOOGLE_CLIENT_SECRET', ''))
except ImportError:
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

# Microsoft Teams Graph API Credentials
try:
    from decouple import config
    TEAMS_TENANT_ID = config('TEAMS_TENANT_ID', default=os.environ.get('TEAMS_TENANT_ID', ''))
    TEAMS_CLIENT_ID = config('TEAMS_CLIENT_ID', default=os.environ.get('TEAMS_CLIENT_ID', ''))
    TEAMS_CLIENT_SECRET = config('TEAMS_CLIENT_SECRET', default=os.environ.get('TEAMS_CLIENT_SECRET', ''))
    TEAMS_ORGANIZER_ID = config('TEAMS_ORGANIZER_ID', default=os.environ.get('TEAMS_ORGANIZER_ID', ''))
except ImportError:
    TEAMS_TENANT_ID = os.environ.get('TEAMS_TENANT_ID', '')
    TEAMS_CLIENT_ID = os.environ.get('TEAMS_CLIENT_ID', '')
    TEAMS_CLIENT_SECRET = os.environ.get('TEAMS_CLIENT_SECRET', '')
    TEAMS_ORGANIZER_ID = os.environ.get('TEAMS_ORGANIZER_ID', '')

import sys
print("DIAGNOSTIC — GOOGLE_CLIENT_ID is set in env:", bool(GOOGLE_CLIENT_ID), file=sys.stderr)
print("DIAGNOSTIC — TEAMS_CLIENT_ID is set in env:", bool(TEAMS_CLIENT_ID), file=sys.stderr)
print("DIAGNOSTIC — All env var names:", [k for k in os.environ.keys() if k.startswith(('GOOGLE', 'TEAMS', 'RAILWAY', 'DATABASE', 'SECRET', 'DEBUG'))], file=sys.stderr)














