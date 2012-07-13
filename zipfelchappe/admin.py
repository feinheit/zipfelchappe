from django import forms
from django.db import models
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from feincms.admin import item_editor

from . import app_settings
from .models import Project, Reward, Receiver, Pledge, Category
from .widgets import AdminImageWidget
from .utils import get_backer_model

class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['title', 'slug']
    prepopulated_fields = {
        'slug': ('title',),
    }

class RewardInlineAdmin(admin.StackedInline):
    model = Reward
    extra = 0
    feincms_inline = True
    fieldsets = [
        [None, {
            'fields': [
                'title',
                ('minimum', 'quantity'),
                'description',
            ]
        }]
    ]

class PledgeInlineAdmin(admin.TabularInline):
    model = Pledge
    extra = 0
    raw_id_fields = ('backer','project')
    feincms_inline = True


class ReceiverInlineFormset(forms.models.BaseInlineFormSet):

    def clean(self):
        super(ReceiverInlineFormset, self).clean()

        total_percent = 0
        num_primary = 0

        for form in self.forms:
            if hasattr(form, 'cleaned_data'):
                total_percent += form.cleaned_data['percent']
                if form.cleaned_data['primary']:
                    num_primary += 1

        if total_percent != 100:
            raise forms.ValidationError(_('Percent must be 100 in total! '
                'Now is %d %%' % total_percent))

        if num_primary != 1:
            raise forms.ValidationError(_('You must define exactly one '
                'primary receiver'))


class ReceiverInlineAdmin(admin.StackedInline):
    model = Receiver
    formset = ReceiverInlineFormset
    extra = 0
    feincms_inline = True


class ProjectAdmin(item_editor.ItemEditor):
    inlines = [RewardInlineAdmin, ReceiverInlineAdmin, PledgeInlineAdmin]
    date_hierarchy = 'end'
    list_display = ['title', 'goal']
    search_fields = ['title', 'slug']
    readonly_fields = ('achieved_pretty',)
    raw_id_fields = ('author',)
    filter_horizontal = ['categories']
    prepopulated_fields = {
        'slug': ('title',),
        }

    formfield_overrides = {
        models.ImageField: {'widget': AdminImageWidget},
    }

    fieldset_insertion_index = 1
    fieldsets = [
        [None, {
            'fields': [
                ('title', 'slug'),
                ('goal', 'currency', 'achieved_pretty'),
                ('start', 'end'),
                'author',
            ]
        }],
        [_('teaser'), {
            'fields': [('teaser_image', 'teaser_text')],
            'classes': ['feincms_inline'],
        }],
        [_('categories'), {
            'fields': ['categories'],
            'classes': ['feincms_inline'],
        }],
        item_editor.FEINCMS_CONTENT_FIELDSET,
    ]

    def achieved_pretty(self, p):
        if p.id:
            return u'%d %s (%d%%)' % (p.achieved, p.currency, p.percent)
        else:
            return u'unknown'
    achieved_pretty.short_description = _('achieved')

    class Media:
        css = { "all" : (
            "zipfelchappe/css/project_admin.css",
            "zipfelchappe/css/feincms_extended_inlines.css",
            "zipfelchappe/css/admin_hide_original.css",
        )}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Project, ProjectAdmin)


class DefaultBackerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    search_fields = ('first_name', 'last_name', 'email')
    raw_id_fields = ['user']
    inlines = [PledgeInlineAdmin]

if app_settings.BACKER_MODEL == 'zipfelchappe.Backer':
    BackerModel = get_backer_model()
    admin.site.register(BackerModel, DefaultBackerAdmin)
