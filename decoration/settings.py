"""
Django settings for decoration project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+nij4fikst76nks4u)h6r*a5o1157sn*e_na7ghftwl=)=hwt!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['auconfort.shop', 'samydeco.com', 'www.auconfort.shop', 'www.samydeco.com',]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts',
    'ecommerce',

    'axes',
    'widget_tweaks',
    'rest_framework',
    'requests',
    'django_seed',
    'bootstrap_modal_forms',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ecommerce.middleware.CartIdentifierMiddleWare',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'decoration.urls'

AUTH_USER_MODEL = 'accounts.User'

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

WSGI_APPLICATION = 'decoration.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'decoration',
        'USER': 'postgres',
        'PASSWORD': 'Simouche',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 180000,
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

CACHES = {
    'default': {
        'BACKEND': None,
    }
}

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
    'base_backend.authentication.PhoneOrEmailBackend'
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'fr'

LANGUAGES = [
    ('fr', _('Français')),
    ('en', _('English')),
    ('ar', _('العربية')),
]

LOCALE_PATHS = [
    BASE_DIR / "locale"
]

TIME_ZONE = 'Africa/Algiers'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TIME_INPUT_FORMATS = ('%H:%M',)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '../static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
MEDIA_URL = '/uploads/'

APP_NAME = "ECOMMERCE"

# PHONE_VERIFICATION_OTP_TABLE = "restaurants.SmsVerification"
# PASSWORD_RESET_TABLE = "restaurants.PasswordReset"

LOGIN_URL = 'accounts:login'

# EMAIL_HOST = 'skylight-ds.com'
# EMAIL_PORT = '587'
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'support@skylight-ds.com'
# EMAIL_HOST_PASSWORD = 'Algerie@2019@'
# SERVER_EMAIL = 'support@skylight-ds.com'


# axes configs
AXES_FAILURE_LIMIT = 150 if DEBUG else 5  # change this to a callable function from DB.
AXES_COOLOFF_TIME = 1
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_LOCKOUT_TEMPLATE = None  # lockout template
AXES_RESET_ON_SUCCESS = True
