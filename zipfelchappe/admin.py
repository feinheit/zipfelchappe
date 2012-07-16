from django.contrib import admin

from . import app_settings
from .models import Project, ProjectAdmin, PledgeInlineAdmin, Category
from .utils import get_backer_model, use_default_backer_model

class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['title', 'slug']
    prepopulated_fields = {
        'slug': ('title',),
    }


class DefaultBackerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    search_fields = ('first_name', 'last_name', 'email')
    raw_id_fields = ['user']
    inlines = [PledgeInlineAdmin]


if use_default_backer_model():
    BackerModel = get_backer_model()
    admin.site.register(BackerModel, DefaultBackerAdmin)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Project, ProjectAdmin)
