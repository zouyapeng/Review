"""
Django settings for b1 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(__file__)

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%^!o7n71c&$ms5#j8c^8hq09jninquna7q))^y!0d70d@pd(k$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
    'cdos',
)

AUTHENTICATION_BACKENDS = (
    'cdos.backend.OAuthBackend',
    'cdos.backend.UserBackend',
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'compresshtml.middleware.CompressHtmlMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

TASTYPIE_DEFAULT_FORMATS = ['json']
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(
    BASE_DIR,
    'static',
)


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

COMPRESS_HTML = True
COMPRESS_ENABLED = True
CBS_URL = "http://172.29.50.21/"
HOME_DIR = "/home/cas/"
PXE = "root@172.29.10.10"
SIGNIN_BACK = "http://172.29.10.110:8000/cdos/api/v1/user/signin/"

auth_uri = "http://172.29.10.110/"
# =========cas=========
CAS_SETTINGS = {
        "client_id": "SM;@1J_YhKlzWu=g51krKseMu_!h2Ht=UdBGEU;J",
        "client_secret": "1zuYtknkucmZ1=1iK-VntoYB3z6QMspDndkMrVy!7:-HTrVE89MZFO;4r.j0QrSJRHRG?:xmC2ZRlZDIqg_2dPfOwPpd4UhcY1hy;j2INUg3H2X0fns@hqdIoE=1i1_B",
        "auth_uri": auth_uri,
        "redirect_uri": SIGNIN_BACK,
        "authorization_uri": "%soauth2/authorize/" % auth_uri,
        "token_uri": "%soauth2/token/" % auth_uri,
        "openid_uri": "%soauth2/me/" % auth_uri,
        "user_api_uri": "%soauth2/api/v1/user/" % auth_uri,
}

