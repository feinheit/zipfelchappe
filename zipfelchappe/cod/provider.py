# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from ..payment_provider import BasePaymentProvider


class CodProvider(BasePaymentProvider):
    """
    The Payment Provider for wire transfer (ESR).
    """

    def __unicode__(self):
        return unicode(_('Wire transfer'))

    def payment_url(self):
        return reverse('zipfelchappe_cod_payment')

    def collect_pledge(self, pledge):
        pass

    def validate_project(self, project, db_instance=None):
        pass

    def refund_pledge(self, pledge):
        pass

    def get_provider_url_patterns(self):
        return []

    def refund_payments(self, project):
        pass