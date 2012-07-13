from django.contrib import admin

from .models import Preapproval, Payment

class PreapprovalAdmin(admin.ModelAdmin):
    model = Preapproval
    list_display = ('pledge', 'key', 'amount', 'status', 'approved', 'sender')
    list_filter = ('pledge__project__title', 'approved')
    readonly_fields = ('created', 'modified')
    search_fields = ('key', 'sender')

admin.site.register(Preapproval, PreapprovalAdmin)
