"""
Payment settings for Postfinance payments

Needs the following settings to work correctly::

    ZIPFELCHAPPE_POSTFINANCE = {
        'PSPID': 'your_postfinance_id',
        'LIVE': True, # Or False
        'SHA1_IN': 'yourhash',
        'SHA1_OUT': 'yourotherhash',
    }
"""
from django.conf import settings

# Fallback values
POSTFINANCE = {
    'PSPID': '',
    'LIVE': False,
    'SHA1_IN': '',
    'SHA1_OUT': '',
}

POSTFINANCE.update(getattr(settings, 'ZIPFELCHAPPE_POSTFINANCE', {}))
