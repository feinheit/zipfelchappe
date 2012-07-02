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
    #os.path.join(APP_BASEDIR, 'zipfelchappe', 'static'),
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

ROOT_URLCONF = 'zipfelchappe.urls'

WSGI_APPLICATION = 'zipfelchappe.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(APP_BASEDIR, 'zipfelchappe', 'templates'),
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
    
    'south',
    'towel',
    
    'zipfelchappe'
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

if DEBUG:
    LOGGING['loggers']['django.request'] = {
        'handlers': ['console'],
        'level': 'DEBUG',
        }



DEFAULT_KEYSTORE = os.path.join(APP_BASEDIR, 'default.keystore')


try:
    from local_settings import *
except ImportError:
    pass
