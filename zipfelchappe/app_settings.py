
from django.conf import settings

CURRENCIES = getattr(settings, 'ZIPFELCHAPPE_CURRENCIES',
    ('CHF', 'EUR', 'USD'))

DISQUS_SHORTNAME = getattr(settings, 'ZIPFELCHAPPE_DISQUS_SHORTNAME', None)

ALLOW_ANONYMOUS_PLEDGES = getattr(settings, 'ZIPFECHAPPE_ALLOW_ANONYMOUS_PLEDGES', True)
