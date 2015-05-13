from __future__ import absolute_import, unicode_literals

from django.contrib import admin

from . import models

class CodPaymentAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'pledge']

admin.site.register(models.CodPayment, CodPaymentAdmin)
