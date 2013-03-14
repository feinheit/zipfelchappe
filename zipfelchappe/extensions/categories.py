from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from feincms import extensions

from ..models import Category


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['title', 'slug']
    prepopulated_fields = {
        'slug': ('title',),
    }


class Extension(extensions.Extension):
    ident = 'categories'

    def handle_model(self):
        self.model.add_to_class('categories', models.ManyToManyField(Category,
            verbose_name=_('categories'), related_name='projects',
            null=True, blank=True)
        )

    def handle_modeladmin(self, modeladmin):
        admin.site.register(Category, CategoryAdmin)

        modeladmin.fieldsets.insert(2, [
            _('categories'), {
                'fields': ['categories'],
                'classes': ['feincms_inline'],
            }
        ])

        modeladmin.filter_horizontal.append('categories')
