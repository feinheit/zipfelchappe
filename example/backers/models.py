import datetime
from dateutil import relativedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from zipfelchappe.models import BackerBase

class ExtendedBacker(BackerBase):

    GENDER_CHOICES = (
        ('m', _('Male')),
        ('f', _('Female')),
    )

    gender = models.CharField(_('gender'), choices=GENDER_CHOICES, max_length=1)

    #birth_date = models.DateField(_('birth date'), blank=True, null=True)

    address = models.CharField(_('address'), max_length=100)
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state'), max_length=100)
    zip = models.CharField(_('zip'), max_length=10)
    country = models.CharField(_('country'), max_length=100)

    class Meta:
        verbose_name = _('backer')
        verbose_name_plural = _('backer')

    @property
    def age(self):
        TODAY = datetime.date.today()
        if self.birth_date:
            return u"%s" % relativedelta.relativedelta(TODAY, self.birth_date).years
        else:
            return None
