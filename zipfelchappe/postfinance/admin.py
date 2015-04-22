
from django.contrib import admin

from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    def status_text(self, obj):
        return obj.status_text()

    list_display = ('order_id', 'amount', 'currency', 'status_text', 'updated')
    list_filter = ('pledge__project',)
    readonly_fields = (
        'amount',
        'currency',
        'PAYID',
        'STATUS',
        'status_text',
        'PM',
        'ACCEPTANCE',
        'CARDNO',
        'BRAND',
    )

admin.site.register(Payment, PaymentAdmin)
