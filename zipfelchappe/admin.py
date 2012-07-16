from django.contrib import admin

from . import app_settings
from .models import Project, ProjectAdmin, PledgeInlineAdmin
from .utils import get_backer_model, use_default_backer_model

class DefaultBackerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    search_fields = ('first_name', 'last_name', 'email')
    raw_id_fields = ['user']
    inlines = [PledgeInlineAdmin]


if use_default_backer_model():
    BackerModel = get_backer_model()
    admin.site.register(BackerModel, DefaultBackerAdmin)

admin.site.register(Project, ProjectAdmin)
