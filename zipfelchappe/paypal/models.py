

from django.db import models
from django.utils.translation import ugettext_lazy as _

class PreapprovalKey(models.Model):

    ACTIVE = 'ACTIVE'
    CANCELED = 'CANCELED'
    DEACTIVATED = 'DEACTIVATED'

    STATUS_CHOICES = ((s, s) for s in (ACTIVE, CANCELED, DEACTIVATED))

    key = models.CharField(_('key'), max_length=20)

    pledge = models.OneToOneField('zipfelchappe.Pledge', related_name='preapprovalkey')

    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES)

    approved = models.BooleanField(_('approved'))

    sender = models.EmailField(_('sender'))

    data = models.TextField(_('data'), blank=True)

    class Meta:
        verbose_name = _('preapproval key')
        verbose_name_plural = _('preapproval keys')

    def __unicode__(self):
        return self.key


class Payment(models.Model):

    CREATED = 'CREATED'
    COMPLETED = 'COMPLETED'
    INCOMPLETE = 'INCOMPLETE'
    ERROR = 'ERROR'
    REVERSALERROR = 'REVERSALERROR'
    PROCESSING = 'PROCESSING'
    PENDING = 'PENDING'

    STATUS_CHOICES = ((s, s) for s in (CREATED, COMPLETED, INCOMPLETE, ERROR,
        REVERSALERROR, PROCESSING, PENDING))

    key = models.CharField(_('key'), max_length=20)

    preapproval_key = models.ForeignKey('PreapprovalKey',
        related_name='payments')

    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES)

    data = models.TextField(_('data'), blank=True)

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __unicode__(self):
        return self.key
