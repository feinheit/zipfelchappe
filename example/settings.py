import os
import sys

WEBAPP_DIR = os.path.dirname(os.path.abspath(__file__))
APP_BASEDIR = os.path.abspath(os.path.join(WEBAPP_DIR, os.path.pardir))
DEBUG = any((cmd in sys.argv for cmd in (
    'runserver', 'shell', 'dbshell', 'sql', 'sqlall')))
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('FEINHEIT Developers', 'dev@feinheit.ch'),
)

MANAGERS = ADMINS

DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(APP_BASEDIR, 'base.db'),
    'USER': '',
    'PASSWORD': '',
    'HOST': '',
    'PORT': '',
}}

TIME_ZONE = 'Europe/Zurich'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = False

MEDIA_ROOT = os.path.join(APP_BASEDIR, 'uploads')
MEDIA_URL = '/uploads/'

STATIC_ROOT = os.path.join(APP_BASEDIR, 'static')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(WEBAPP_DIR, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'example.urls'

TEMPLATE_DIRS = (
    os.path.join(WEBAPP_DIR, 'templates')
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",

    # required by django-admin-tools
    'django.core.context_processors.request',

    'allauth.account.context_processors.account',
    'allauth.socialaccount.context_processors.socialaccount'
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

AUTH_PROFILE_MODULE = 'accounts.UserProfile'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',

    'fhadmin',
    'feincms',
    'feincms.module.medialibrary',
    'emailconfirmation',
    'uni_form',
    'south',
    'towel',

    'allauth',
    'allauth.account',
    #'allauth.socialaccount',
    #'allauth.socialaccount.providers.facebook',
    #'allauth.socialaccount.providers.openid',
    #'allauth.socialaccount.providers.twitter',
    #'allauth.socialaccount.providers.google',
    #'allauth.socialaccount.providers.github',
    #'allauth.socialaccount.providers.linkedin',

    'zipfelchappe',

    'example',
    'example.accounts',
)

from fhadmin import FHADMIN_GROUPS_REMAINING
_ = lambda x: x

FHADMIN_GROUPS_CONFIG = [
    (_('Main'), {
        'apps': ('zipfelchappe',),
        }),
    (_('Modules'), {
        'apps': (FHADMIN_GROUPS_REMAINING),
        }),
    (_('Preferences'), {
        'apps': ('auth', 'sites'),
        }),
    ]

FEINCMS_RICHTEXT_INIT_CONTEXT = {
    'TINYMCE_JS_URL': '/static/tinymce/jscripts/tiny_mce/tiny_mce_dev.js',
    }

try:
    from local_settings import *
except ImportError:
    pass
