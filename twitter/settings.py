"""
Django settings for twitter project.

Generated by 'django-admin startproject' using Django 3.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
from kombu import Queue
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ot)o!87!8wer+44f4ac0whx#4fl#v(_x*b0!nfa2k_c4k5m$@9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', '192.168.33.10', 'localhost']

INTERNAL_IPS = ['10.0.2.2']

# Application definition

INSTALLED_APPS = [
    # django default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party packages
    'rest_framework',
    'debug_toolbar',
    'django_filters',
    'notifications',

    # project apps
    'accounts',
    'tweets',
    'friendships',
    'newsfeeds',
    'comments',
    'likes',
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'twitter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'twitter.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'twitter',
        'HOST': '0.0.0.0',
        'PORT': '3306',
        'USER': 'root',
        'PASSWORD': 'yourpassword',    # 这里是自己下载mysql时候输入两次的那个密码
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# AUTH_USER_MODEL = 'django.contrib.auth.models.User'

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
MEDIA_ROOT = 'media/'

# config upload file storage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
TESTING = ((" ".join(sys.argv)).find('manage.py test') != -1)
if TESTING:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# config BUCKET_NAME and REGION NAME
AWS_STORAGE_BUCKET_NAME = 'django-twitter-ping'
AWS_S3_REGION_NAME = 'us-west-1'

# https://docs.djangoproject.com/en/3.1/topics/cache/
# sudo apt-get install memcached
# use 'pip install python-memcached'
# don't pip install memcache or django-memcached
CACHES = {
        'default': {
                'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
                'LOCATION': '127.0.0.1:11211',
                'TIMEOUT': 86400
        },
        'testing': {
                'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
                'LOCATION': '127.0.0.1:11211',
                'TIMEOUT': 86400,
                'KEY_PREFIX': 'testing',
        },
        'ratelimit': {
                'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
                'LOCATION':'127.0.0.1:11211',
                'TIMEOUT': 86400 * 7,
                'KEY_PREFIX': 'rl',
        },
}

# Redis
# install: sudo apt-get install redis
# then install redis python client: pip install redis
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0 if TESTING else 1
REDIS_KEY_EXPIRE_TIME = 7 * 86400 # in seconds
REDIS_LIST_LENGTH_LIMIT = 1000 if not TESTING else 20

# Celery Configuration Options
# use comment below to run worker process on different machine
# celery -A twitter worker -l INFO
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/2' if not TESTING else 'redis://127.0.0.1:6379/0'
CELERY_TIMEZONE = "UTC"
CELERY_TASK_ALWAYS_EAGER = TESTING
CELERY_QUEUES = (
    Queue('default', routing_key='default'),
    Queue('newsfeeds', routing_key='newsfeeds'),
)

try:
    from .local_settings import *
except:
    pass
