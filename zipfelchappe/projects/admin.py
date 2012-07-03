from django.contrib import admin
from models import Project, ProjectAdmin

admin.site.register(Project, ProjectAdmin)
