from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    PAYPAL_USERID = settings.ZIPFELCHAPPE_PAYPAL_USERID
except AttributeError:
    raise ImproperlyConfigured('You MUST define ZIPFELCHAPPE_PAYPAL_USERID in settings!')

try:
    PAYPAL_PASSWORD = settings.ZIPFELCHAPPE_PAYPAL_PASSWORD
except AttributeError:
    raise ImproperlyConfigured('You MUST define ZIPFELCHAPPE_PAYPAL_PASSWORD in settings!')

try:
    PAYPAL_SIGNATURE = settings.ZIPFELCHAPPE_PAYPAL_SIGNATURE
except AttributeError:
    raise ImproperlyConfigured('You MUST define ZIPFELCHAPPE_PAYPAL_SIGNATURE in settings!')

try:
    PAYPAL_SIGNATURE = settings.ZIPFELCHAPPE_PAYPAL_SIGNATURE
except AttributeError:
    raise ImproperlyConfigured('You MUST define ZIPFELCHAPPE_PAYPAL_SIGNATURE in settings!')


PAYPAL_APPLICATIONID = getattr(settings, 'ZIPFELCHAPPE_PAYPAL_APPLICATIONID', None)


PAYPAL_LIVE = getattr(settings, 'ZIPFELCHAPPE_PAYPAL_LIVE', False)
