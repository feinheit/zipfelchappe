
from django.conf import settings

CURRENCIES = getattr(settings, 'CURRENCIES', ('CHF', 'EUR', 'USD'))
