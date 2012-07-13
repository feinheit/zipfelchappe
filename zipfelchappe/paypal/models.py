from django.db import models
from django.utils.translation import ugettext_lazy as _

from zipfelchappe.fields import CurrencyField
from zipfelchappe.base import CreateUpdateModel

class Preapproval(CreateUpdateModel):

    pledge = models.OneToOneField('zipfelchappe.Pledge',
        related_name='preapproval')

    key = models.CharField(_('key'), unique=True, db_index=True, max_length=20)

    amount = CurrencyField(_('amount'), max_digits=10, decimal_places=2)

    status = models.CharField(_('status'), max_length=20, blank=True, null=True)

    approved = models.BooleanField(_('approved'), default=False)

    sender = models.EmailField(_('sender'), blank=True, null=True)

    data = models.TextField(_('data'), blank=True)

    class Meta:
        verbose_name = _('preapproval')
        verbose_name_plural = _('preapprovals')

    def __unicode__(self):
        return self.key


class Payment(CreateUpdateModel):

    key = models.CharField(_('key'), max_length=20)

    preapproval = models.ForeignKey('Preapproval',
        related_name='payments')

    status = models.CharField(_('status'), max_length=20, blank=True, null=True)

    data = models.TextField(_('data'), blank=True)

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __unicode__(self):
        return self.key
