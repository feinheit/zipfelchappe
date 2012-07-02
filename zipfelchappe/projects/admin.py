from django.contrib import admin
from models import Project, Reward
from orderable_inlines import OrderableTabularInline

class RewardInlineAdmin(OrderableTabularInline):
    model = Reward
    extra = 1
    orderable_field = 'order'

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'goal')
    inlines = [RewardInlineAdmin,]

admin.site.register(Project, ProjectAdmin)
