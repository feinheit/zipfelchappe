from django.contrib import admin

from feincms.admin import item_editor

from orderable_inlines import OrderableTabularInline

from zipfelchappe.models import Project, Reward, Payment


class RewardInlineAdmin(OrderableTabularInline):
    model = Reward
    extra = 0
    orderable_field = 'order'

class PaymentInlineAdmin(admin.TabularInline):
    model = Payment
    extra = 0

class ProjectAdmin(item_editor.ItemEditor):
    inlines = [RewardInlineAdmin, PaymentInlineAdmin]
    date_hierarchy = 'end'
    list_display = ['title', 'goal']
    search_fields = ['title', 'slug']
    prepopulated_fields = {
        'slug': ('title',),
        }

    fieldset_insertion_index = 1
    fieldsets = [
        [None, {
            'fields': [
                ('title', 'slug'),
                'goal',
                ('start', 'end'),
            ]
        }],
        item_editor.FEINCMS_CONTENT_FIELDSET,
    ]


admin.site.register(Project, ProjectAdmin)
