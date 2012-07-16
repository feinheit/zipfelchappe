from django import forms
from django.db import models
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ..base import CreateUpdateModel

class Receiver(CreateUpdateModel):

    project = models.ForeignKey('zipfelchappe.Project', related_name='receivers')

    email = models.CharField(_('email'), max_length=100)

    percent = models.PositiveSmallIntegerField(_('percent'))

    primary = models.BooleanField(_('primary'))

    class Meta:
        app_label = 'zipfelchappe'
        verbose_name = _('paypal receiver')
        verbose_name_plural = _('paypal receivers')

    def __unicode__(self):
        return self.email


class ReceiverInlineFormset(forms.models.BaseInlineFormSet):

    def clean(self):
        super(ReceiverInlineFormset, self).clean()

        total_percent = 0
        num_primary = 0

        for form in self.forms:
            if hasattr(form, 'cleaned_data'):
                total_percent += form.cleaned_data['percent']
                if form.cleaned_data['primary']:
                    num_primary += 1

        if self.forms and total_percent != 100:
            raise forms.ValidationError(_('Percent must be 100 in total! '
                'Now is %d %%' % total_percent))

        if self.forms and num_primary != 1:
            raise forms.ValidationError(_('You must define exactly one '
                'primary receiver'))


class ReceiverInlineAdmin(admin.StackedInline):
    model = Receiver
    formset = ReceiverInlineFormset
    extra = 0
    feincms_inline = True


def register(cls, admin_cls):
    admin_cls.inlines.insert(1, ReceiverInlineAdmin)
