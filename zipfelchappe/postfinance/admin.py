
from django.contrib import admin

from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'amount', 'currency', 'updated')
    list_filter = ('pledge__project',)
    readonly_fields = (
        'amount',
        'currency',
        'PM',
        'ACCEPTANCE',
        'STATUS',
        'CARDNO',
        'PAYID',
        'NCERROR',
        'BRAND',
    )

admin.site.register(Payment, PaymentAdmin)
