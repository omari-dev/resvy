"""
Django settings for resvy project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from datetime import timedelta
from pathlib import Path

from django.utils.dateparse import parse_time

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-__yxu=*+62c*g_yh-s%e5f1t!)den7bm-+ru++=&9a=4gmz!a='  # TODO: read it from env variable

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    # Health checks
    'health_check',  # required
    'health_check.db',  # stock Django health checkers
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.migrations',
    'health_check.contrib.redis',  # requires Redis broker

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third apps
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'django_extensions',
    'drf_spectacular',
    'coverage',
    # LOCAL_APPS
    'users',
    'reservations'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'resvy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'resvy.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_NAME', 'resvy_db'),
        'USER': os.environ.get('POSTGRES_USER', 'resvy'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'resvy'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_PERMISSION_CLASSES': (),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'PAGE_SIZE': 100,
    'TIME_FORMAT': '%I:%M %p',
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'UPDATE_LAST_LOGIN': True,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    "TOKEN_OBTAIN_SERIALIZER": "users.serializers.UserInfoTokenObtainPairSerializer",
}

LOGIN_URL = '/v1/auth/login/'
AUTH_USER_MODEL = 'users.User'

REDIS_CACHE = {
    'BACKEND': 'django_redis.cache.RedisCache',
    'LOCATION': 'redis://{}/'.format(os.environ.get('REDIS_URL', 'redis:6379')),
    'OPTIONS': {
        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        'PASSWORD': os.environ.get('REDIS_PASSWORD', ''),
    },
    'TIMEOUT': int(os.environ.get('CACHE_TIMEOUT', 500)),
}
REDIS_ENABLED = os.getenv('REDIS_ENABLED', 0)

CACHES = {
    'default': REDIS_CACHE if REDIS_ENABLED else {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Rsvy APIs',
    'DESCRIPTION': 'Reservation APIs',
    'VERSION': '0.0.1',
    'SERVE_INCLUDE_SCHEMA': False,
    'SERVERS': [{'url': 'http://127.0.0.1:8000', 'description': 'DEV'}],
    # 'SERVE_PERMISSIONS': ('users.permissions.IsSuperUser',)
    'SCHEMA_PATH_PREFIX': r'/v[0-9]',
}

RESERVATION_STARTING_FROM_TIME = parse_time(os.getenv('RESERVATION_STARTING_FROM_TIME', '12:00'))
RESERVATION_ENDS_AT_TIME = parse_time(os.getenv('RESERVATION_ENDS_AT_TIME', '23:59'))

REDIS_CACHE.get('LOCATION', 'redis://redis:6379')
