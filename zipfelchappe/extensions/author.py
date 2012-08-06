from django.db import models
from django.utils.translation import ugettext_lazy as _

def register(cls, admin_cls):

    cls.add_to_class('author', models.ForeignKey('auth.User',
        verbose_name=_('author'), blank=True, null=True))

    admin_cls.fieldsets[0][1]['fields'].append('author')
    admin_cls.raw_id_fields += ('author',)
