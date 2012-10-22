import csv
from datetime import datetime

from django.contrib import admin
from django.contrib.admin import util
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

from . import app_settings
from .models import Project, ProjectAdmin, Pledge
from .utils import get_backer_model, use_default_backer_model

from .paypal.models import Preapproval, Payment

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
        if f is not None:
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
    raw_id_fields = ('backer','project')
    feincms_inline = True


class DefaultBackerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    search_fields = ('_first_name', '_last_name', '_email', 'user__username', 'user__email')
    raw_id_fields = ['user']
    inlines = [PledgeInlineAdmin]
    actions = [export_as_csv]

if use_default_backer_model():
    BackerModel = get_backer_model()
    admin.site.register(BackerModel, DefaultBackerAdmin)


class RewardListFilter(admin.SimpleListFilter):

    title = _('Reward')
    parameter_name = 'reward'

    def lookups(self, request, model_admin):
        project_id = request.GET.get('project__id__exact', None)
        if  project_id:
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
            ('approved', _('is approved')),
            ('paid', _('is paid'))
        )

    def queryset(self, request, queryset):
        value = self.value()

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

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'amount_display',
        'reward',
        'status'
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
    list_filter = ('project', 'status', PaypalFilter, RewardListFilter)
    actions = [export_as_csv]

admin.site.register(Project, ProjectAdmin)
admin.site.register(Pledge, PledgeAdmin)