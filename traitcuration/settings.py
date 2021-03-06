"""
Django settings for traitcuration project.

Generated by 'django-admin startproject' using Django 3.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import django_heroku
import os
import yaml

from celery.schedules import crontab

try:
    file = open('config.yaml', 'r')
    config = yaml.load(file, Loader=yaml.FullLoader)
except FileNotFoundError as e:
    print('Config file not found! Make sure you have config.yaml in the project directory')
    raise e

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


ALLOWED_HOSTS = config['ALLOWED_HOSTS']


# Application definition

INSTALLED_APPS = [
    'traitcuration.traits.apps.TraitsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'compressor',
    'django_celery_results',
    'celery_progress',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'computedfields',
    'rest_framework',
    'django_admin_conf_vars',
    'django_celery_beat',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'traitcuration.urls'

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

WSGI_APPLICATION = 'traitcuration.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {'default': config['DATABASES']['POSTGRES']}

# Auth
AUTH_USER_MODEL = 'traits.User'

# The id of the 'site' entry in the database, required by django-allauth to know the app's URL.
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

# django-allauth configuration

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = "email"
ACCOUNT_AUTHENTICATION_METHOD = "email"
SOCIALACCOUNT_QUERY_EMAIL = True
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
COMPRESS_ENABLED = True

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'traitcuration/static/'), ]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
COMPRESS_ROOT = os.path.join(BASE_DIR, 'traitcuration/static/')

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    'compressor.finders.CompressorFinder'
)

COMPRESS_PRECOMPILERS = (
    ('text/x-sass', 'django_libsass.SassCompiler'),
    ('text/x-scss', 'django_libsass.SassCompiler'),
)


# Celery config
CELERY_BROKER_URL = config['DATABASES']['REDIS']['URL']
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_IMPORTS = (
    'traitcuration.traits.tasks',
    'traitcuration.traits.datasources',
)

CELERY_BEAT_SCHEDULE = {
    'import-clinvar-every-thursday': {
        'task': 'traitcuration.traits.tasks.import_clinvar',
        'schedule': crontab(hour='9', minute='25', day_of_week='thu'),
    },
    'import-zooma-every-thursday': {
        'task': 'traitcuration.traits.tasks.import_zooma',
        'schedule': crontab(hour='9', minute='33', day_of_week='thu'),
    },
    'update-ols-every-month': {
        'task': 'traitcuration.traits.tasks.import_ols',
        'schedule': crontab(0, 0, day_of_month='2')
    }
}


# django_admin_conf_vars config
VARS_MODULE_PATH = 'traitcuration.config_vars'


# Local environment config
if os.environ.get('DJANGO_ENV') == 'LOCAL_DEV':
    from .settings_localdev import *
elif os.environ.get('DJANGO_ENV') == 'DEV':
    from .settings_dev import *


# API config
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# Activate Django-Heroku, only on Heroku environments.
if '/app' in os.environ['HOME']:
    django_heroku.settings(locals())
