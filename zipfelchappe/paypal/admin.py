from django.contrib import admin

from .models import Preapproval, Payment


class PreapprovalAdmin(admin.ModelAdmin):
    list_display = ('pledge', 'key', 'amount', 'status', 'approved', 'sender')
    list_filter = ('pledge__project', 'approved')
    readonly_fields = ('created', 'modified')
    search_fields = ('key', 'sender')

    def has_add_permission(self, request):
        return False


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('key', 'status')
    list_filter = ('preapproval__pledge__project', 'status')
    search_fields = ('key', 'preapproval_key')
    readonly_fields = ('key', 'preapproval', 'status', 'data')

    def has_add_permission(self, request):
        return False


admin.site.register(Preapproval, PreapprovalAdmin)
admin.site.register(Payment, PaymentAdmin)
