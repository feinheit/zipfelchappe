from django.db import models
from django.utils.translation import ugettext_lazy as _

from feincms import extensions


class Extension(extensions.Extension):
    ident = 'author'

    def handle_model(self):

        self.model.add_to_class('author', models.ForeignKey('auth.User',
            verbose_name=_('author'), blank=True, null=True))

    def handle_modeladmin(self, modeladmin):
        modeladmin.fieldsets[0][1]['fields'].append('author')
        modeladmin.raw_id_fields.append('author')
