import os
import sys

WEBAPP_DIR = os.path.dirname(os.path.abspath(__file__))
APP_BASEDIR = os.path.abspath(os.path.join(WEBAPP_DIR, os.path.pardir))
DEBUG = any((cmd in sys.argv for cmd in (
    'runserver', 'shell', 'dbshell', 'sql', 'sqlall')))

DEBUG = True

SECRET_KEY = os.getenv('SECRET_KEY', 'unsafe_default')

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

_ = lambda s: s

LANGUAGES = (
    ('de', _('German')),
    ('en', _('English')),
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
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'example.urls'

TEMPLATE_DIRS = (
    os.path.join(WEBAPP_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',

    # debug purposes
    # 'debug_toolbar',

    'feincms',
    'feincms.module.page',
    'feincms.module.medialibrary',
    'tinymce',

    'zipfelchappe',
    'zipfelchappe.translations',
    'zipfelchappe.paypal',
    'zipfelchappe.postfinance',

    'example',
    'example.backerprofiles',
)

_ = lambda x: x

ZIPFELCHAPPE_PAYMENT_PROVIDERS = (
    ('paypal', _('Paypal')),
)


ZIPFELCHAPPE_BACKER_PROFILE = 'backerprofiles.BackerProfile'


FEINCMS_RICHTEXT_INIT_CONTEXT = {
    'TINYMCE_JS_URL': '/static/tiny_mce/tiny_mce.js',
    }

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'ENABLE_STACKTRACES' : True,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'paypal_ipn': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(WEBAPP_DIR, 'log', 'paypal_ipn.log'),
        },
        'postfinance_ipn': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(WEBAPP_DIR, 'log', 'postfinance_ipn.log'),
        },
    },
    'loggers': {
        'zipfelchappe.paypal.ipn': {
            'handlers': ['paypal_ipn'],
            'level': 'DEBUG',
        },
        'zipfelchappe.postfinance.ipn': {
            'handlers': ['postfinance_ipn'],
            'level': 'DEBUG',
        },
    }
}

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

try:
    from local_settings import *
except ImportError:
    pass
