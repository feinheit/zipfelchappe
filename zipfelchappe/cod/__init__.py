from __future__ import unicode_literals, absolute_import
from django.apps import AppConfig
from .. import register_provider


class CodConfig(AppConfig):
    name = 'zipfelchappe.cod'
    verbose_name = 'Wire transfer payment backend'

    def ready(self):
        from .provider import CodProvider
        register_provider('cod', CodProvider('cod'))

default_app_config = 'zipfelchappe.cod.CodConfig'
