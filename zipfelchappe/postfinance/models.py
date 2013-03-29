from django.db import models
from django.utils.translation import ugettext_lazy as _

class Payment(models.Model):

    order_id = models.CharField(_('order id'), max_length=100)
    pledge = models.ForeignKey('zipfelchappe.Pledge')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    amount = models.CharField(_('amount'), max_length=20, editable=False,
        blank=True)
    currency = models.CharField(_('currency'), max_length=10, editable=False,
        blank=True)

    PM = models.CharField(max_length=100, editable=False, blank=True)
    ACCEPTANCE = models.CharField(max_length=100, editable=False, blank=True)
    STATUS = models.CharField(max_length=100, editable=False, blank=True)
    CARDNO = models.CharField(max_length=100, editable=False, blank=True)
    PAYID = models.CharField(max_length=100, editable=False, blank=True)
    NCERROR = models.CharField(max_length=100, editable=False, blank=True)
    BRAND = models.CharField(max_length=100, editable=False, blank=True)

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __unicode__(self):
        return self.order_id
