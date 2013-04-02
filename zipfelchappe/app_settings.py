
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

CURRENCIES = getattr(settings, 'ZIPFELCHAPPE_CURRENCIES',
    ('CHF', 'EUR', 'USD'))

DISQUS_SHORTNAME = getattr(settings, 'ZIPFELCHAPPE_DISQUS_SHORTNAME', None)

PAGINATE_BY = getattr(settings, 'ZIPFELCHAPPE_PAGINATE_BY', 10)

ALLOW_ANONYMOUS_PLEDGES = getattr(settings, 'ZIPFELCHAPPE_ALLOW_ANONYMOUS_PLEDGES', True)

PAYMENT_PROVIDERS = getattr(settings, 'ZIPFELCHAPPE_PAYMENT_PROVIDERS',
    (
        ('paypal', _('Paypal')),
    )
)
