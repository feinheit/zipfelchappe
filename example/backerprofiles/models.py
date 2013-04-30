
from django.db import models
from django.utils.translation import ugettext_lazy as _

#from zipfelchappe.models import Backer

class BackerProfile(models.Model):

    backer = models.OneToOneField('zipfelchappe.Backer')

    street = models.CharField(_('Street'), max_length=100)
    zip = models.CharField(_('ZIP'), max_length=100)
    city = models.CharField(_('City'), max_length=100)