from django.contrib import admin

from .models import Preapproval, Payment

class PreapprovalAdmin(admin.ModelAdmin):
    list_display = ('pledge', 'key', 'amount', 'status', 'approved', 'sender')
    list_filter = ('pledge__project__title', 'approved')
    readonly_fields = ('created', 'modified')
    search_fields = ('key', 'sender')


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('key', 'status')

admin.site.register(Preapproval, PreapprovalAdmin)
admin.site.register(Payment, PaymentAdmin)
