from __future__ import unicode_literals, absolute_import
from django.apps import AppConfig
from .. import register_provider


class PaypalConfig(AppConfig):
    name = 'zipfelchappe.paypal'
    verbose_name = 'Paypal payment backend'
    
    def ready(self):
        from .provider import PaypalProvider
        register_provider('paypal', PaypalProvider('paypal'))

default_app_config = 'zipfelchappe.paypal.PaypalConfig'
