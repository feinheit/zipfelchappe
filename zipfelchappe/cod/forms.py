from __future__ import absolute_import, unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import CodPayment


class RequestPaymentSlipForm(forms.Form):
    payment = forms.ModelChoiceField(CodPayment.objects.all(), widget=forms.HiddenInput())
    first_name = forms.CharField(label=_('first name'))
    last_name = forms.CharField(label=_('last name'))
    address = forms.CharField(label=_('address'))
    zip_code = forms.CharField(label=_('zip code'))
    city = forms.CharField(label=_('city'))
