import os
import sys

WEBAPP_DIR = os.path.dirname(os.path.abspath(__file__))
APP_BASEDIR = os.path.abspath(os.path.join(WEBAPP_DIR, os.path.pardir))
DEBUG = any((cmd in sys.argv for cmd in (
    'runserver', 'shell', 'dbshell', 'sql', 'sqlall')))

DEBUG = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('FEINHEIT Developers', 'dev@feinheit.ch'),
)

MANAGERS = ADMINS

INTERNAL_IPS = ['127.0.0.1']

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

_ = lambda x : x

LANGUAGES = (
    ('en', _('English')),
    ('de', _('German')),
)

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

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
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'fhprojects.middleware.ForceDomainMiddleware',
    'fhprojects.middleware.MobileDetectionMiddleware',
)

ROOT_URLCONF = 'fhprojects.urls'

TEMPLATE_DIRS = (
    os.path.join(WEBAPP_DIR, 'templates')
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'fhprojects.context_processors.fhweb',
    'feincms.context_processors.add_page_if_missing',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

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
    'feincms.module.page',
    'feincms.module.medialibrary',
    'mptt',
    'south',

    'fhprojects',

    #'zipfelchappe',
    #'zipfelchappe.paypal',
)

#ZIPFELCHAPPE_BACKER_MODEL = 'backers.ExtendedBacker'

GOOGLE_ANALYTICS = 'UA-1621887-16'

from fhadmin import FHADMIN_GROUPS_REMAINING
_ = lambda x: x

FHADMIN_GROUPS_CONFIG = [
    (_('Main'), {
        'apps': ('zipfelchappe','backers', 'paypal'),
        }),
    (_('Modules'), {
        'apps': (FHADMIN_GROUPS_REMAINING,),
        }),
    (_('Preferences'), {
        'apps': ('auth', 'sites'),
        }),
    ]

FEINCMS_RICHTEXT_INIT_CONTEXT = {
    'TINYMCE_JS_URL': '/static/lib/tinymce/tiny_mce.js',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'paypal_ipn': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(APP_BASEDIR, 'log', 'paypal_ipn.log'),
        },
    },
    'loggers': {
        'zipfelchappe.paypal.ipn': {
            'handlers': ['paypal_ipn'],
            'level': 'INFO',
        },
    }
}


try:
    from local_settings import *
except ImportError:
    pass
