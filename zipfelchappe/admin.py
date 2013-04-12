import csv
from datetime import datetime

from django import forms
from django.conf.urls import patterns, url
from django.db import models
from django.contrib import admin
from django.contrib.admin import util
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

from feincms.admin import item_editor

from .models import Project, Pledge, Backer, Update, Reward, MailTemplate
from .widgets import AdminImageWidget, TestMailWidget

from .paypal.models import Preapproval, Payment
from .app_settings import PAYMENT_PROVIDERS


def export_as_csv(modeladmin, request, queryset):
    model = modeladmin.model
    response = HttpResponse(mimetype='text/csv')
    model_name = force_unicode(model._meta.verbose_name)
    timestamp = datetime.now().strftime('%d%m%y_%H%M')
    filename = '%s_export_%s.csv' % (model_name, timestamp)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    writer = csv.writer(response)
    field_names = modeladmin.list_display

    def get_label(field):
        label = util.label_for_field(field, model, modeladmin)
        return force_unicode(label).title().encode('utf-8')

    def serialize(field, obj):
        f, attr, value = util.lookup_field(field, obj, modeladmin)
        if f is not None and not isinstance(f, models.BooleanField):
            value = util.display_for_field(value, f)
        return force_unicode(value).encode('utf-8')

    writer.writerow([get_label(field) for field in field_names])

    for obj in queryset:
        writer.writerow([serialize(field, obj) for field in field_names])

    return response

export_as_csv.short_description = _('Export as csv')


class PledgeInlineAdmin(admin.TabularInline):
    model = Pledge
    extra = 0
    raw_id_fields = ('backer', 'project')
    feincms_inline = True


class BackerAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email')
    list_display_links = ('user', 'first_name', 'last_name', 'email')
    search_fields = ('_first_name', '_last_name', '_email', 'user__username', 'user__email')
    raw_id_fields = ['user']
    inlines = [PledgeInlineAdmin]
    actions = [export_as_csv]

admin.site.register(Backer, BackerAdmin)


class RewardListFilter(admin.SimpleListFilter):

    title = _('Reward')
    parameter_name = 'reward'

    def lookups(self, request, model_admin):
        project_id = request.GET.get('project__id__exact', None)
        if project_id:
            project = get_object_or_404(Project, pk=project_id)
            for reward in project.rewards.all():
                name = '{0} {1}'.format(reward.minimum, project.currency)
                yield (str(reward.pk), name)

    def queryset(self, request, queryset):
        value = self.value()

        if value:
            return queryset.filter(reward__id=value)


class PaypalFilter(admin.SimpleListFilter):

    title = _('Paypal status')
    parameter_name = 'paypal'

    def lookups(self, request, model_admin):
        return (
            ('inactive', _('approval inactive')),
            ('approved', _('is approved')),
            ('paid', _('is paid'))
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value == 'inactive':
            inactive = Preapproval.objects.filter(approved=False)
            inactive_ids = inactive.values_list('pledge__pk')
            return queryset.filter(pk__in=inactive_ids)
        if value == 'approved':
            approved = Preapproval.objects.filter(approved=True)
            approved_ids = approved.values_list('pledge__pk')
            return queryset.filter(pk__in=approved_ids)
        if value == 'paid':
            paid = Payment.objects.filter(status=Payment.COMPLETED)
            paid_ids = paid.values_list('preapproval__pledge__pk')
            return queryset.filter(pk__in=paid_ids)


class PledgeAdmin(admin.ModelAdmin):

    def username(self, pledge):
        if pledge.backer and pledge.backer.user:
            return pledge.backer.user.username
        else:
            return _('(None)')
    username.short_description = _('username')

    def first_name(self, pledge):
        if pledge.backer:
            return pledge.backer.first_name
        else:
            return _('(None)')
    first_name.short_description = _('first name')

    def last_name(self, pledge):
        if pledge.backer:
            return pledge.backer.last_name
        else:
            return _('(None)')
    last_name.short_description = _('last name')

    def email(self, pledge):
        if pledge.backer:
            return pledge.backer.email
        else:
            return _('(None)')
    email.short_description = _('email')

    def amount_display(self, pledge):
        return '%s %s' % (pledge.amount, pledge.currency)
    amount_display.short_description = _('amount')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super(PledgeAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

        project = getattr(request, '_obj', None)

        if db_field.name == 'reward':
            if request._obj is not None:
                field.queryset = field.queryset.filter(project=project.project)
            else:
                field.queryset = field.queryset.none()
                field.help_text = _('Save pledge first to select a reward')

        return field

    def get_form(self, request, obj=None, **kwargs):
        request._obj = obj
        return super(PledgeAdmin, self).get_form(request, obj, **kwargs)

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'amount_display',
        'reward',
        'status',
        'provider',
    )

    list_display_links = (
        'username',
        'email',
    )

    search_fields = (
        'backer___first_name',
        'backer___last_name',
        'backer___email',
        'backer__user__username',
        'backer__user__first_name',
        'backer__user__last_name',
        'backer__user__email',
    )

    raw_id_fields = ('backer', 'project')
    list_filter = (
        'project',
        'status',
        'provider',
        PaypalFilter,
        RewardListFilter
    )
    actions = [export_as_csv]



class UpdateInlineAdmin(admin.StackedInline):
    model = Update
    extra = 0
    feincms_inline = True
    ordering = ('created',)
    formfield_overrides = {
        models.TextField: {
            'widget': forms.Textarea(attrs={'class': 'tinymce'})
        },
    }


class RewardInlineAdmin(admin.StackedInline):
    model = Reward
    extra = 0
    feincms_inline = True
    fieldsets = [
        [None, {
            'fields': [
                ('minimum', 'quantity'),
                'description',
                'reserved',
            ]
        }]
    ]

    readonly_fields = ('reserved',)


class MailTemplateForm(forms.ModelForm):
    test_mail = forms.EmailField(required=False, widget=TestMailWidget())

    class Meta:
        model = MailTemplate


class MailTemplateInlineAdmin(admin.StackedInline):
    model = MailTemplate
    form = MailTemplateForm
    extra = 0
    max_num = len(MailTemplate.ACTION_CHOICES)
    feincms_inline = True

    formfield_overrides = {
        models.CharField: {
            'widget': forms.TextInput(attrs={'class': 'vLargeTextField'})
        },
    }

    class Media:
        js = ('zipfelchappe/js/email_test.js',)


class ProjectAdmin(item_editor.ItemEditor):
    inlines = [UpdateInlineAdmin, RewardInlineAdmin, MailTemplateInlineAdmin]
    date_hierarchy = 'end'
    list_display = ['position', 'title', 'goal']
    list_display_links = ['title']
    list_editable = ['position']
    list_filter = []
    raw_id_fields = []
    filter_horizontal = []
    search_fields = ['title', 'slug']
    readonly_fields = ['achieved_pretty']
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
            ]
        }],
        [_('teaser'), {
            'fields': [('teaser_image', 'teaser_text')],
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

    def get_urls(self):
        from zipfelchappe import admin_views
        urls = patterns('',
            url(r'^send_test_mail/$', 
                self.admin_site.admin_view(admin_views.send_test_mail), 
                name='zipfelchappe_send_test_mail'
            ),
            url(r'^(?P<project_id>\d+)/collect_pledges/$',
                self.admin_site.admin_view(admin_views.collect_pledges),
                name='zipfelchappe_project_collect_pledges'
            ),
            url(r'^(?P<project_id>\d+)/authorized_pledges/$',
                self.admin_site.admin_view(admin_views.authorized_pledges),
                name='zipfelchappe_project_authorized_pledges'
            ),
            url(r'^(?P<project_id>\d+)/collect_pledge/(?P<pledge_id>\d+)/$',
                self.admin_site.admin_view(admin_views.collect_pledge),
                name='zipfelchappe_project_collect_pledge'
            ),
        )
        return urls + super(ProjectAdmin, self).get_urls()

    class Media:
        css = {"all": (
            "zipfelchappe/css/project_admin.css",
            "zipfelchappe/css/feincms_extended_inlines.css",
            "zipfelchappe/css/admin_hide_original.css",
        )}
        js = (
            'zipfelchappe/lib/jquery-1.9.1.min.js',
            'zipfelchappe/lib/jquery-ui-1.10.2.min.js',
            'zipfelchappe/js/admin_order.js',
            'zipfelchappe/js/tinymce_init.js',
            'zipfelchappe/js/reward_check_deletable.js',
        )


admin.site.register(Project, ProjectAdmin)
admin.site.register(Pledge, PledgeAdmin)
