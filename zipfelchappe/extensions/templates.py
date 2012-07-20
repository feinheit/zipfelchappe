from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..base import CreateUpdateModel

OVERRIDEABLE_TEMPLATES = {
    'zipfelchappe/paypal/thankyou.html': {
        'type': 'html',
        'name': _('Thank you page'),
        'preview_url': 'blub',
    }
}

TEMPLATE_CHOICES = ((k, v['name']) for k, v in OVERRIDEABLE_TEMPLATES.items())


class Template(CreateUpdateModel):

    project = models.ForeignKey('Project', verbose_name=_('project'),
        related_name='templates')

    name = models.CharField(_('name'), max_length=100, choices=TEMPLATE_CHOICES)

    content = models.TextField(_('content'), blank=True)

    class Meta:
        app_label = 'zipfelchappe'
        verbose_name = _('template')
        verbose_name_plural = _('templates')

    def __unicode__(self):
        return self.name

class TemplateAdmin(admin.StackedInline):
    model = Template
    feincms_inline = True
    extra = 0

def register(cls, admin_cls):
    admin_cls.inlines.insert(2, TemplateAdmin)
