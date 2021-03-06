"""
Django settings for service_provider project.
Generated by 'django-admin startproject' using Django 3.1.6.
For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from datetime import timedelta
from pathlib import Path
from service_provider.config import ConfigDb
from service_provider.config import ConfigFirebase
import os
import configuration
from firebase_admin import db
import firebase_admin
from firebase_admin import credentials
import django_heroku

# Initilizing firebase with credential
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": ConfigFirebase.type,
        "project_id": ConfigFirebase.project_id,
        "private_key_id": ConfigFirebase.private_key_id,
        "private_key": ConfigFirebase.private_key,
        "client_email":ConfigFirebase.client_email,
        "client_id": ConfigFirebase.client_id,
        "auth_uri": ConfigFirebase.auth_uri,
        "token_uri": ConfigFirebase.token_uri,
        "auth_provider_x509_cert_url": ConfigFirebase.auth_provider_x509_cert_url,
        "client_x509_cert_url": ConfigFirebase.client_x509_cert_url
    })
    defaul_app = firebase_admin.initialize_app(cred,{
        'databaseURL':ConfigFirebase.databaseURL
    })

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3ufel4yt7qv311_vhwym9jji6ahdbirx&wfadlq&9e9p043sk*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['ec2-18-222-75-85.us-east-2.compute.amazonaws.com','smartaisolutions.net','localhost','localhost:8000','localhost:3000','127.0.0.1','ec2-18-221-157-224.us-east-2.compute.amazonaws.com','sasserviceprovider.herokuapp.com']
CORS_ALLOW_ALL_ORIGINS=True 
CORS_ORIGIN_ALLOW_ALL = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'authorization',
    'corsheaders',
    'leads',
    'transactions',
    'django_extensions',
    'django_rest_passwordreset',
    'dashboard',
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware'
]

ROOT_URLCONF = 'service_provider.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'service_provider.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DATE_INPUT_FORMATS': ['%Y-%m-%dT%H:%M:%S.%f%z']
}

DJANGO_REST_PASSWORDRESET_TOKEN_CONFIG = {
    "CLASS": "django_rest_passwordreset.tokens.RandomNumberTokenGenerator",
    "OPTIONS": {
        "min_number": 1500,
        "max_number": 9999
    }
}
DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME = 0.125
# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': ConfigDb.DB_NAME,
        'USER': ConfigDb.USER,
        'PASSWORD': ConfigDb.PASSWORD,
        'HOST': 'localhost'
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
AUTH_USER_MODEL = 'authorization.user'

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


EMAIL_HOST = configuration.EMAIL_HOST
EMAIL_PORT = configuration.EMAIL_PORT
EMAIL_HOST_USER = configuration.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = configuration.EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = True

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = 'static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_ROOT=os.path.join(BASE_DIR,'service_provider/service_provider/media')
STATICFILES_STORAGE='whitenoise.storage.CompressedManifestStaticFilesStorage'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=60)
}

django_heroku.settings(locals())
