import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from . import app_settings
from .models import Project, ProjectAdmin, PledgeInlineAdmin
from .utils import get_backer_model, use_default_backer_model

def export_as_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export.csv'
    writer = csv.writer(response)
    field_names = modeladmin.list_display
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response

export_as_csv.short_description = _('Export as csv')


class DefaultBackerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    search_fields = ('first_name', 'last_name', 'email')
    raw_id_fields = ['user']
    inlines = [PledgeInlineAdmin]
    actions = [export_as_csv]

if use_default_backer_model():
    BackerModel = get_backer_model()
    admin.site.register(BackerModel, DefaultBackerAdmin)

admin.site.register(Project, ProjectAdmin)
