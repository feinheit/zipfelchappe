from django.contrib import admin
from zipfelchappe.models import Project, ProjectAdmin

admin.site.register(Project, ProjectAdmin)
