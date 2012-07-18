from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..models import Category

class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['title', 'slug']
    prepopulated_fields = {
        'slug': ('title',),
    }


def register(cls, admin_cls):
    admin.site.register(Category, CategoryAdmin)

    cls.add_to_class('categories', models.ManyToManyField(Category,
        verbose_name=_('categories'), related_name='projects',
        null=True, blank=True)
    )

    admin_cls.fieldsets.insert(2, [
        _('categories'), {
            'fields': ['categories'],
            'classes': ['feincms_inline'],
        }
    ])

    admin_cls.filter_horizontal += ('categories',)
