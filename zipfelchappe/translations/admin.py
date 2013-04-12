
from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin
from django.db import models
from django.conf.urls import patterns
from django.utils.translation import ugettext_lazy as _

from .models import *

from ..widgets import TestMailWidget

from feincms.admin import item_editor


class LimitTranslationOfMixin(object):

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(RewardTransAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

        project = getattr(request, '_obj', None)

        if db_field.name == 'translation_of':
            if request._obj is not None:
                field.queryset = field.queryset.filter(project=project.project)
            else:
                field.queryset = field.queryset.none()

        return field


class RewardTransAdmin(admin.StackedInline, LimitTranslationOfMixin):
    model = RewardTranslation
    feincms_inline = True
    extra = 0


class UpdateTransAdmin(admin.StackedInline, LimitTranslationOfMixin):
    model = UpdateTranslation
    feincms_inline = True
    extra = 0
    formfield_overrides = {
        models.TextField: {
            'widget': forms.Textarea(attrs={'class': 'tinymce'})
        },
    }


class MailTemplateForm(forms.ModelForm):
    test_mail = forms.EmailField(required=False, widget=TestMailWidget())

    class Meta:
        model = MailTemplateTranslation


class MailTemplateTransAdmin(admin.StackedInline, LimitTranslationOfMixin):
    model = MailTemplateTranslation
    form = MailTemplateForm
    feincms_inline = True
    extra = 0

    formfield_overrides = {
        models.CharField: {
            'widget': forms.TextInput(attrs={'class': 'vLargeTextField'})
        },
    }

    class Media:
        js = ('zipfelchappe/js/email_test.js',)


class ProjectTransAdmin(item_editor.ItemEditor):
    inlines = [UpdateTransAdmin, RewardTransAdmin, MailTemplateTransAdmin]
    raw_id_fields = ('translation_of',)
    list_filter = ('translation_of', 'lang')

    fieldsets = [
        [None, {
            'fields': [
                ('translation_of', 'lang'),
                'title',
            ]
        }],
        [_('teaser'), {
            'fields': [('teaser_text')],
            'classes': ['feincms_inline'],
        }],
        item_editor.FEINCMS_CONTENT_FIELDSET,
    ]

    def get_urls(self):
        from zipfelchappe import admin_views
        urls = patterns('',
            url(r'^send_test_mail/$', 
                self.admin_site.admin_view(admin_views.send_test_mail), 
                name='zipfelchappe_translation_send_test_mail'),
        )
        return urls + super(ProjectTransAdmin, self).get_urls()

    class Media:
        css = {"all": (
            "zipfelchappe/css/feincms_extended_inlines.css",
            "zipfelchappe/css/admin_hide_original.css",
            "zipfelchappe/css/translation_admin.css",
        )}
        js = (
            'lib/jquery-1.7.2.min.js',
            'lib/jquery-ui-1.8.21.min.js',
            'zipfelchappe/js/tinymce_init.js',
        )

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj = obj
        return super(ProjectTransAdmin, self).get_form(request, obj, **kwargs)

admin.site.register(ProjectTranslation, ProjectTransAdmin)
