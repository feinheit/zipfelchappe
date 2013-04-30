"""
Payment settings for paypal payments

Needs the following settings to work correctly::

    ZIPFELCHAPPE_PAYPAL = {
        'USERID': 'paypal_api_user_id',
        'PASSWORD': 'paypal_api_password',
        'SIGNATURE': 'paypal_api_signature',
        'APPLICATIONID': 'granted_application_id' # Only if you are live
        'LIVE': True, # Or False
        'RECEIVERS': [{
            'email': 'your@paypalid.ch',
            'percent': 100,
        }]
    }
"""
from django.conf import settings

# Fallback values
PAYPAL = {
    'USERID': '',
    'PASSWORD': '',
    'SIGNATURE': '',
    'APPLICATIONID': None,
    'LIVE': False,
    'RECEIVERS': [],
}

PAYPAL.update(getattr(settings, 'ZIPFELCHAPPE_PAYPAL', {}))
