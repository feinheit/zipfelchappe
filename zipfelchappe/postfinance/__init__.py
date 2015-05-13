from __future__ import unicode_literals, absolute_import
from django.apps import AppConfig
from .. import register_provider

class PostfinanceConfig(AppConfig):
    name = 'zipfelchappe.postfinance'
    verbose_name = 'Postfinance payment backend'

    def ready(self):
        from .provider import PostfinanceProvider
        register_provider('postfinance', PostfinanceProvider('postfinance'))

default_app_config = 'zipfelchappe.postfinance.PostfinanceConfig'
