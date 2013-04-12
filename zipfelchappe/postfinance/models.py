from django.db import models
from django.utils.translation import ugettext_lazy as _


STATUS_DICT = {
    '0' : 'Incomplete or invalid',
    '1' : 'Cancelled by client',
    '2' : 'Authorization refused',
    '4' : 'Order stored',
    '41': 'Waiting client payment',
    '5' : 'Authorized',
    '51': 'Authorization waiting',
    '52': 'Authorization not known',
    '55': 'Stand-by',
    '59': 'Authoriz. to get manually',
    '6' : 'Authorized and cancelled',
    '61': 'Author. deletion waiting',
    '62': 'Author. deletion uncertain',
    '63': 'Author. deletion refused',
    '64': 'Authorized and cancelled',
    '7' : 'Payment deleted',
    '71': 'Payment deletion pending',
    '72': 'Payment deletion uncertain',
    '73': 'Payment deletion refused',
    '74': 'Payment deleted',
    '75': 'Deletion processed by merchant',
    '8' : 'Refund',
    '81': 'Refund pending',
    '82': 'Refund uncertain',
    '83': 'Refund refused',
    '84': 'Payment declined by the acquirer',
    '85': 'Refund processed by merchant',
    '9' : 'Payment requested',
    '91': 'Payment processing',
    '92': 'Payment uncertain',
    '93': 'Payment refused',
    '94': 'Refund declined by the acquirer',
    '95': 'Payment processed by merchant',
    '99': 'Being processed',
}


class Payment(models.Model):

    order_id = models.CharField(_('order id'), max_length=100)
    pledge = models.OneToOneField('zipfelchappe.Pledge', 
        related_name='postfinance_payment')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    amount = models.CharField(_('amount'), max_length=20, blank=True)
    currency = models.CharField(_('currency'), max_length=10, blank=True)

    PAYID = models.CharField(max_length=100, blank=True)
    STATUS = models.CharField(max_length=100, blank=True)

    PM = models.CharField(max_length=100, blank=True)
    ACCEPTANCE = models.CharField(max_length=100, blank=True)
    CARDNO = models.CharField(max_length=100, blank=True)
    BRAND = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __unicode__(self):
        return self.order_id

    def status_text(self):
        return STATUS_DICT.get(self.STATUS, _('unknown'))
