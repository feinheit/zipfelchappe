# coding: utf-8
from __future__ import absolute_import, unicode_literals
import factory

from zipfelchappe.cod.models import CodPayment

class CodPaymentFactory(factory.DjangoModelFactory):

    class Meta:
        model = CodPayment
