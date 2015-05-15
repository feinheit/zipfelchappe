from __future__ import absolute_import, unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from zipfelchappe.base import CreateUpdateModel


class CodPayment(CreateUpdateModel):
    pledge = models.OneToOneField(
        'zipfelchappe.Pledge', related_name='cod_payment')

    payment_received = models.DateField(_('payment received'), null=True)

    payment_slip_requested = models.BooleanField(
        _('payment slip requested'), default=False, blank=True)
    payment_slip_sent = models.BooleanField(
        _('payment slip sent'), default=False, blank=True)

    payment_slip_first_name = models.CharField(
        _('first name'), max_length=50, blank=True)
    payment_slip_last_name = models.CharField(
        _('last name'), max_length=50, blank=True)
    payment_slip_address = models.CharField(
        _('address'), max_length=200, blank=True)
    payment_slip_zip_code = models.CharField(
        _('zip code'), max_length=20, blank=True)
    payment_slip_city = models.CharField(
        _('city'), max_length=50, blank=True)

    class Meta:
        verbose_name = _('cod payment')
        verbose_name_plural = _('cod payments')
        app_label = 'zipfelchappe'
        ordering = ['modified']

    def __unicode__(self):
        return '{0} {1}'.format(
            self.pledge.backer.first_name, self.pledge.backer.last_name)
