
from django.conf import settings

CURRENCIES = getattr(settings, 'ZIPFELCHAPPE_CURRENCIES',
    ('CHF', 'EUR', 'USD'))

DISQUS_SHORTNAME = getattr(settings, 'ZIPFELCHAPPE_DISQUS_SHORTNAME', None)

PAGINATE_BY = getattr(settings, 'ZIPFELCHAPPE_PAGINATE_BY', 10)

ALLOW_ANONYMOUS_PLEDGES = getattr(settings, 'ZIPFECHAPPE_ALLOW_ANONYMOUS_PLEDGES', True)
