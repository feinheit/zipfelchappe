from __future__ import unicode_literals, absolute_import
import csv
import ast
from datetime import datetime

from django import forms
from django.conf.urls import patterns, url
from django.db import models
from django.db.models.loading import get_model
from django.contrib import admin
from django.contrib.admin import util
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _


from feincms.admin import item_editor

from .models import Project, Pledge, Backer, Update, Reward, MailTemplate
from .models import ExtraField
from .widgets import AdminImageWidget, TestMailWidget
from .utils import get_user_search_fields

from .paypal.models import Preapproval, Payment  # TODO: remove dependency on paypal
from .app_settings import BACKER_PROFILE


def export_as_csv(modeladmin, request, queryset):
    model = modeladmin.model
    response = HttpResponse(mimetype='text/csv')
    model_name = force_unicode(model._meta.verbose_name)
    timestamp = datetime.now().strftime('%d%m%y_%H%M')
    filename = '%s_export_%s.csv' % (model_name, timestamp)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    writer = csv.writer(response)
    excluded = getattr(modeladmin, 'export_excluded', [])
    field_names = set(modeladmin.list_display) - set(excluded)

    def get_label(field):
        label = util.label_for_field(field, model, modeladmin)
        return force_unicode(label).title().encode('utf-8')

    def serialize(field, obj):
        f, attr, value = util.lookup_field(field, obj, modeladmin)
        if f is not None and not isinstance(f, models.BooleanField):
            value = util.display_for_field(value, f)
        return force_unicode(value).encode('utf-8')

    header_row = [get_label(field) for field in field_names]

    if queryset.count() > 0:
        first = queryset[0]
        if hasattr(first, 'export_related'):
            header_row += first.export_related().keys()

    writer.writerow(header_row)

    for obj in queryset:
        field_values = [serialize(field, obj) for field in field_names]

        if callable(getattr(obj, 'export_related', False)):
            field_values += obj.export_related().values()

        if hasattr(obj, 'extradata'):
            try:
                data = ast.literal_eval(obj.extradata)
            except SyntaxError:
                data = {}
            values = [v.encode('utf-8') for v in data.values()]
            field_values += values

        writer.writerow(field_values)

    return response

export_as_csv.short_description = _('Export as csv')


class PledgeInlineAdmin(admin.TabularInline):
    model = Pledge
    extra = 0
    raw_id_fields = ('backer', 'project')
    exclude = ('extradata',)
    feincms_inline = True


class BackerAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'first_name', 'last_name', 'full_name')
    list_display_links = ('user', 'email')
    search_fields = []  # Dynamically set in __init__
    raw_id_fields = ['user']
    inlines = [PledgeInlineAdmin]
    actions = [export_as_csv]

    def __init__(self, *args, **kwargs):
        ''' Dynamically generate search_fields values

        Due to the possibility of custom user models the search fields
        cant't be set statically.
        '''
        super(BackerAdmin, self).__init__(*args, **kwargs)
        for field_name in get_user_search_fields():
            self.search_fields.append('user__{0}'.format(field_name))


if BACKER_PROFILE:
    try:
        app_label, model_name = BACKER_PROFILE.split('.')
        profile_model = get_model(app_label, model_name)
        if profile_model is not None:
            class BackerProfileAdmin(admin.StackedInline):
                model = profile_model

            BackerAdmin.inlines.insert(0, BackerProfileAdmin)
    except ImportError:
        pass

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


# TODO: remove dependency on paypal
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
    def __init__(self, *args, **kwargs):
        ''' Dynamically generate search_fields values

        Due to the possibility of custom user models the search fields
        cant't be set statically.
        '''
        super(PledgeAdmin, self).__init__(*args, **kwargs)
        for field_name in get_user_search_fields():
            self.search_fields.append('backer__user__{0}'.format(field_name))

    def username(self, pledge):
        if pledge.backer and pledge.backer.user:
            return pledge.backer.user
        else:
            return _('(None)')
    username.short_description = _('username')

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

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        obj = self.get_object(request, util.unquote(object_id))
        if not obj:
            raise Http404()
        ExtraForm = obj.project.extraform()

        try:
            extra_data = ast.literal_eval(obj.extradata)
        except SyntaxError:
            extra_data = {}

        if request.method == 'POST':
            extra_form = ExtraForm(request.POST)
            if extra_form.is_valid():
                obj.extradata = extra_form.clean()
                obj.save()
        else:
            extra_form = ExtraForm(initial=extra_data)

        extra_context['extraform'] = extra_form

        return super(PledgeAdmin, self).change_view(request, object_id,
            form_url, extra_context=extra_context)

    def extradata_display(self, pledge):
        try:
            data = ast.literal_eval(pledge.extradata)
            display = ''
            for key, value in data.items():
                display += '<div><strong>%s:</strong> %s</div>' % (key, value)
            return display
        except:
            return pledge.extradata
    extradata_display.allow_tags = True
    extradata_display.short_description = 'Extra Data'

    list_display = (
        'username',
        '_email',
        '_first_name',
        '_last_name',
        'amount_display',
        'anonymously',
        'reward',
        'status',
        'provider',
        'created',
    )

    export_excluded = ('extradata_display',)

    list_display_links = (
        'username',
        '_email',
        '_first_name',
        '_last_name',
    )

    search_fields = []  # Set dynamically in __init__

    raw_id_fields = ('backer', 'project')
    list_filter = (
        'project',
        'status',
        'provider',
        PaypalFilter,
        RewardListFilter
    )
    actions = [export_as_csv]
    readonly_fields = ['extradata', '_email', '_first_name', '_last_name',
                       'details', 'anonymously', 'amount', 'project', 'backer', 'provider']


class UpdateInlineAdmin(admin.StackedInline):
    model = Update
    extra = 0
    feincms_inline = True
    ordering = ('created',)
    formfield_overrides = {
        models.TextField: {
            'widget': forms.Textarea(attrs={'class': 'item-richtext'})
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
        # TODO: validate
        fields = ['project', 'action', 'subject', 'template', 'test_mail']


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


class ExtraFieldInlineAdmin(admin.TabularInline):
    model = ExtraField
    feincms_inline = True
    prepopulated_fields = {'name': ('title',)}
    extra = 0


class ProjectAdmin(item_editor.ItemEditor):
    inlines = [UpdateInlineAdmin, RewardInlineAdmin, MailTemplateInlineAdmin,
               ExtraFieldInlineAdmin]
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
        from . import admin_views
        urls = patterns(
            '',
            url(r'^(?P<project_id>\d+)/send_test_mail/$',
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


admin.site.register(Project, ProjectAdmin)
admin.site.register(Pledge, PledgeAdmin)
