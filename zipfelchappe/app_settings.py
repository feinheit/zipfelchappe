from __future__ import absolute_import, unicode_literals
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

CURRENCIES = getattr(settings, 'ZIPFELCHAPPE_CURRENCIES', ('CHF', 'EUR', 'USD'))

DISQUS_SHORTNAME = getattr(settings, 'ZIPFELCHAPPE_DISQUS_SHORTNAME', None)

PAGINATE_BY = getattr(settings, 'ZIPFELCHAPPE_PAGINATE_BY', 10)
PAGINATE_BACKERS_BY = getattr(settings, 'ZIPFELCHAPPE_PAGINATE_BACKERS', 25)

ALLOW_ANONYMOUS_PLEDGES = getattr(settings, 'ZIPFELCHAPPE_ALLOW_ANONYMOUS_PLEDGES', True)

BACKER_PROFILE = getattr(settings, 'ZIPFELCHAPPE_BACKER_PROFILE', None)

PAYMENT_PROVIDERS = getattr(settings, 'ZIPFELCHAPPE_PAYMENT_PROVIDERS', (
                            ('paypal', _('Paypal')),
                            ))

ROOT_URLS = getattr(settings, 'ZIPFELCHAPPE_URLS', 'zipfelchappe.urls')

DEFAULT_IMAGE_URL = getattr(settings, 'ZIPFELCHAPPE_PLACEHOLDER_IMAGE_URL', '')

USER_FIRST_NAME_FIELD = getattr(
    settings, 'ZIPFELCHAPPE_USER_FIRST_NAME_FIELD', 'first_name')
USER_LAST_NAME_FIELD = getattr(
    settings, 'ZIPFELCHAPPE_USER_LAST_NAME_FIELD', 'last_name')
USER_EMAIL_FIELD = getattr(
    settings, 'ZIPFELCHAPPE_USER_EMAIL_FIELD', 'email')

MAX_PROJECT_DURATION_DAYS = getattr(settings, 'ZIPFELCHAPPE_MAX_PROJECT_DURATION', 120)
