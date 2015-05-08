from __future__ import unicode_literals, absolute_import
from datetime import timedelta

from django import forms

from django.conf import settings
from django.core.exceptions import ValidationError

from django.db import models
from django.db.models import signals, Sum
from django.db.models.fields import AutoField
from django.db.models.fields.related import RelatedField

from django.template.defaultfilters import slugify

from django.utils.datastructures import SortedDict
from django.utils.functional import curry, cached_property
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language
from django.utils.timezone import now

from feincms.contrib.richtext import RichTextField
from feincms.models import Base
from feincms.management.checker import check_database_schema as check_db_schema
from feincms.utils.queryset_transform import TransformQuerySet
from feincms.content.application import models as app_models

from .app_settings import (
        CURRENCIES, PAYMENT_PROVIDERS, BACKER_PROFILE, ROOT_URLS,
        USER_EMAIL_FIELD, USER_FIRST_NAME_FIELD, USER_LAST_NAME_FIELD,
        DEFAULT_IMAGE_URL
)

from .base import CreateUpdateModel
from .fields import CurrencyField
import warnings

CURRENCY_CHOICES = list(((cur, cur) for cur in CURRENCIES))


class TranslatedMixin(object):
    """ Returns a translation object if available, self otherwise """
    @property
    def translated(self):
        if hasattr(self, '_translation'):
            return self._translation
        else:
            filters = {'translation_of': self}
            if hasattr(self, 'project'):
                filters['translation__lang'] = get_language()
            else:
                filters['lang'] = get_language()
            try:
                self._translation = self.translations.get(**filters)
            except:  # TODO: narrow exceptions
                self._translation = self

            return self._translation


class Backer(models.Model):
    """ The base model for all project backers with some transient attributes
        to overwrite user attributes. This is only necessary to support offline
        pledges that were not created on the platform itself. """
    user = models.ForeignKey(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), blank=True,
        null=True, unique=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _('backer')
        verbose_name_plural = _('backers')

    def __unicode__(self):
        return self.full_name

    @cached_property
    def email(self):
        if self.user:
            email = getattr(self.user, USER_EMAIL_FIELD, '')
        else:
            email = ''
        return email

    @cached_property
    def first_name(self):
        if self.user:
            first_name = getattr(self.user, USER_FIRST_NAME_FIELD, '')
        else:
            first_name = ''
        return first_name

    @cached_property
    def last_name(self):
        if self.user:
            last_name = getattr(self.user, USER_LAST_NAME_FIELD, '')
        else:
            last_name = ''
        return last_name

    @cached_property
    def full_name(self):
        if self.user:
            try:
                full_name = self.user.get_full_name()
            except AttributeError:
                full_name =''
            if not full_name:
                full_name = ' '.join([self.first_name, self.last_name])
        else:
            full_name = ''
        return full_name

    def get_profile(self):
        """ Returns the backer profile if available or None """
        if not hasattr(self, '_profile_cache'):
            from .app_settings import BACKER_PROFILE
            try:
                app_label, model_name = BACKER_PROFILE.split('.')
                model = models.get_model(app_label, model_name)
                self._profile_cache = model._default_manager.get(
                    backer__id=self.id)
            except:  # TODO: narrow exception
                return None
        return self._profile_cache

PAYMENT_PROVIDERS += (
    ('offline', _('Offline')),
    ('fake', _('Fake')),
)
DEFAULT_PAYMENT_PROVIDER = PAYMENT_PROVIDERS[0][0]


class Pledge(CreateUpdateModel, TranslatedMixin):
    """ The connection between a backer and a project. One pledge corresponds
        exactly with one payment for a project. The payment itself however is
        tracked in the provider implementation. Based on the outcoming of the
        payment process, the payment provider must change the pledge status. """

    FAILED = 0
    UNAUTHORIZED = 10
    AUTHORIZED = 20
    PROCESSING = 25
    PAID = 30

    STATUS_CHOICES = (
        (UNAUTHORIZED, _('Unauthorized')),
        (AUTHORIZED, _('Authorized')),
        (PAID, _('Paid')),
        (PROCESSING, _('Processing...')),
        (FAILED, _('Failed')),
    )

    # The following fields are filled when pledge is linked with
    # backer/user. The values need to be stored on pledge in case the
    # account gets deleted before the payments are collected. The fields
    # should not be used for anything else. The fields are not on the
    # backer model because the backer model gets created only once per
    # user, but the user can change his name in his profile (and
    # pledge's created after this should use this new name)
    _first_name = models.CharField(_('first name'), max_length=30, blank=True)
    _last_name = models.CharField(_('last name'), max_length=30, blank=True)
    _email = models.EmailField(_('e-mail address'), blank=True)

    backer = models.ForeignKey('Backer', verbose_name=_('backer'),
        related_name='pledges', blank=True, null=True)

    project = models.ForeignKey('Project', verbose_name=_('project'),
        related_name='pledges')

    amount = CurrencyField(_('amount'), max_digits=10, decimal_places=2)

    currency = models.CharField(_('currency'), max_length=3,
        choices=CURRENCY_CHOICES, editable=False, default=CURRENCY_CHOICES[0])

    reward = models.ForeignKey('Reward', blank=True, null=True,
        related_name='pledges')

    anonymously = models.BooleanField(_('anonymously'), default=False, blank=True,
        help_text=_('You will not appear in the backer list'))

    provider = models.CharField(_('payment provider'), max_length=20,
        choices=PAYMENT_PROVIDERS, default=DEFAULT_PAYMENT_PROVIDER)

    # A JSON field for additional data.
    extradata = models.TextField(_('extra'), blank=True)

    details = models.TextField(_('details'), default='')

    # The internal status of the pledge, common for all payment providers
    status = models.PositiveIntegerField(_('status'), choices=STATUS_CHOICES,
            default=UNAUTHORIZED)

    class Meta:
        verbose_name = _('pledge')
        verbose_name_plural = _('pledges')
        ordering = ['-created']

    def __init__(self, *args, **kwargs):
        super(Pledge, self).__init__(*args, **kwargs)
        if 'backer' in kwargs:
            self.set_backer(kwargs['backer'])

    def __unicode__(self):
        return 'Pledge of %d %s from %s to %s' % \
            (self.amount, self.currency, self.backer, self.project)

    def save(self, *args, **kwargs):
        self.currency = self.project.currency
        super(Pledge, self).save(*args, **kwargs)

    def set_backer(self, backer):
        """ Save user data to pledge.
        This needed in case the user deletes his account or changes
        his name in his profile
        """
        self.backer = backer
        self._email = backer.email
        self._first_name = backer.first_name
        self._last_name = backer.last_name

    def add_details(self, details):
        self.details += (details + '\n')

    def mark_failed(self, message=None):
        """
        Setter function to be called on a payment error.
        :param message: Optional error message.
        """
        if self.status > self.FAILED:
            self.status = self.FAILED
            self.reward = None
            if message:
                self.add_details(message)
            self.save()

    @property
    def amount_display(self):
        return u'%s %s' % (self.amount, self.currency)

    @cached_property
    def backer_name(self):
        """
        Get the name of the backer or empty string for anonymous backers
        """
        if self.anonymously:
            return ''
        else:
            return self.backer.full_name

    def export_related(self):
        related_values = {}

        if self.backer and self.backer.get_profile():
            profile = self.backer.get_profile()
            for f in profile._meta.fields:
                if not issubclass(f.__class__, (AutoField, RelatedField)):
                    field_name = unicode(f.verbose_name)
                    value = getattr(profile, f.name)
                    if isinstance(value, basestring):
                        value = value.encode('utf-8')
                    related_values[field_name] = value
        elif BACKER_PROFILE:
            app_label, model_name = BACKER_PROFILE.split('.')
            ProfileModel = models.get_model(app_label, model_name)
            for f in ProfileModel._meta.fields:
                if not issubclass(f.__class__, (AutoField, RelatedField)):
                    field_name = unicode(f.verbose_name)
                    related_values[field_name] = None

        return related_values


class Reward(CreateUpdateModel, TranslatedMixin):
    """ A reward is a give-away for backers that pledge a certain amount.
        Rewards may be limited to a maximum number of backers. """

    project = models.ForeignKey('Project', verbose_name=_('project'),
        related_name='rewards')

    minimum = CurrencyField(_('minimum'), max_digits=10, decimal_places=2,
        help_text=_('How much does one have to donate to receive this?'))

    description = models.TextField(_('description'), blank=True)  # No richtext

    quantity = models.IntegerField(_('quantity'), blank=True, null=True,
        help_text=_('How many times can this award be given away? ' +
            'Empty or 0 means unlimited.'))

    class Meta:
        verbose_name = _('reward')
        verbose_name_plural = _('rewards')
        ordering = ['minimum']

    def __unicode__(self):
        return u'%s on %s (%d)' % (self.minimum, self.project, self.pk)

    def clean(self):
        if self.id and self.quantity and self.quantity < self.awarded:
            raise ValidationError(_('Cannot reduce quantity to a lower value ' +
                'than what was already promised to backers'))

    @property
    def reserved(self):
        return self.pledges.filter(status__gte=Pledge.UNAUTHORIZED).count()

    @property
    def awarded(self):
        return self.pledges.filter(status__gte=Pledge.AUTHORIZED).count()

    @property
    def available(self):
        return self.quantity - self.reserved

    @property
    def is_available(self):
        if not self.quantity:
            return True
        else:
            return self.available > 0


class Category(CreateUpdateModel):
    """ Simple categorisation model for projects """

    title = models.CharField(_('title'), max_length=100)

    slug = models.SlugField(_('slug'), unique=True)

    ordering = models.SmallIntegerField(_('ordering'), default=0)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['ordering']

    def __unicode__(self):
        return self.title

    @app_models.permalink
    def get_absolute_url(self):
        return 'zipfelchappe_project_category_list', ROOT_URLS, (self.slug,)

    @property
    def project_count(self):
        return self.projects.count()


def update_upload_to(instance, filename):
    return (u'projects/%s/updates/%s' % (instance.project.slug, filename)).lower()


class Update(CreateUpdateModel, TranslatedMixin):
    """ Updates are compareable to blog entries about a project """

    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'

    STATUS_CHOICES = (
        (STATUS_DRAFT, _('Draft')),
        (STATUS_PUBLISHED, _('Published')),
    )

    project = models.ForeignKey('Project', verbose_name=_('project'),
        related_name='updates')

    title = models.CharField(_('title'), max_length=100)

    status = models.CharField(_('status'), max_length=20,
        choices=STATUS_CHOICES, default='draft')
    mails_sent = models.BooleanField(editable=False, default=False)

    image = models.ImageField(_('image'), blank=True, null=True,
        upload_to=update_upload_to)

    external = models.URLField(_('external content'), blank=True, null=True,
         help_text=_('Check http://embed.ly/providers for more details'),
    )

    content = RichTextField(_('content'), blank=True)

    attachment = models.FileField(_('attachment'), blank=True, null=True,
        upload_to=update_upload_to)

    class Meta:
        verbose_name = _('update')
        verbose_name_plural = _('updates')
        ordering = ('-created',)

    def __unicode__(self):
        return self.title

    @app_models.permalink
    def get_absolute_url(self):
        return ('zipfelchappe_update_detail', ROOT_URLS,
            (self.project.slug, self.pk)
        )

    @property
    def number(self):
        if hasattr(self, 'num'):
            return self.num
        updates = self.project.updates.filter(status=Update.STATUS_PUBLISHED)
        for index, item in enumerate(reversed(updates)):
            if item == self:
                self.num = index + 1
                return self.num
        return None


class MailTemplate(CreateUpdateModel, TranslatedMixin):
    """ Content override of mails that are sent on specific actions """

    ACTION_THANKYOU = 'thankyou'

    ACTION_CHOICES = (
        (ACTION_THANKYOU, _('Thank you')),
    )

    project = models.ForeignKey('Project', related_name='mail_templates')

    action = models.CharField(_('action'), max_length=30,
        choices=ACTION_CHOICES, default=ACTION_THANKYOU)

    subject = models.CharField(_('subject'), max_length=200)

    template = models.TextField(_('template'))  # no richtext here

    class Meta:
        verbose_name = _('email')
        verbose_name_plural = _('emails')
        unique_together = (('project', 'action'),)

    def __unicode__(self):
        return '%s mail for %s' % (self.action, self.project)


class ExtraField(models.Model):
    """ Extra fields are used to request additional per pledge """

    FIELD_TYPES = [
        ('text', _('text'), forms.CharField),
        ('email', _('e-mail address'), forms.EmailField),
        ('longtext', _('long text'),
         curry(forms.CharField, widget=forms.Textarea)),
        ('checkbox', _('checkbox'), curry(forms.BooleanField, required=False)),
        ('select', _('select'), curry(forms.ChoiceField, required=False)),
    ]

    project = models.ForeignKey('zipfelchappe.Project',
        related_name='extrafields')

    title = models.CharField(_('title'), max_length=100)
    name = models.CharField(_('name'), max_length=100)
    type = models.CharField(
        _('type'), max_length=20, choices=[r[:2] for r in FIELD_TYPES])
    choices = models.CharField(
        _('choices'), max_length=1024, blank=True,
        help_text=_('Comma-separated'))
    help_text = models.CharField(
        _('help text'), max_length=1024, blank=True,
        help_text=_('Optional extra explanatory text beside the field'))
    default_value = models.CharField(
        _('default value'), max_length=255, blank=True,
        help_text=_('Optional default value of the field'))
    is_required = models.BooleanField(_('is required'), default=True)

    class Meta:
        unique_together = (('project', 'name'),)
        verbose_name = _('pledge field')
        verbose_name_plural = _('pledge fields')

    def __unicode__(self):
        return self.title

    def clean(self):
        if self.choices and not isinstance(self.get_type(), forms.ChoiceField):
            raise forms.ValidationError(
                _("You can't specify choices for %s fields") % self.type)

    def get_choices(self):
        get_tuple = lambda val: (slugify(val.strip()), val.strip())
        choices = [get_tuple(value) for value in self.choices.split(',')]
        if not self.is_required and self.type == 'select':
            choices = models.fields.BLANK_CHOICE_DASH + choices
        return tuple(choices)

    def get_type(self, **kwargs):
        types = dict((r[0], r[2]) for r in self.FIELD_TYPES)
        return types[self.type](**kwargs)

    def add_formfield(self, fields, form):
        fields[slugify(self.name)] = self.formfield()

    def formfield(self):
        kwargs = dict(label=self.title, required=self.is_required,
            initial=self.default_value)
        if self.choices:
            kwargs['choices'] = self.get_choices()
        if self.help_text:
            kwargs['help_text'] = self.help_text
        return self.get_type(**kwargs)


class ProjectManager(models.Manager):

    def get_queryset(self):
        return TransformQuerySet(self.model, using=self._db)

    def online(self):
        return self.filter(start__lte=now)

    def funding(self):
        return self.online().filter(end__gte=now)

    def billable(self):
        """ Returns a list of projects that are successfully financed
            (payments can be collected) """
        ending = self.filter(end__lte=now())
        return list([project for project in ending if project.is_financed])


def teaser_img_upload_to(instance, filename):
    return (u'projects/%s/%s' % (instance.slug, filename)).lower()


class Project(Base, TranslatedMixin):
    """ The heart of zipfelchappe. Projects are time limited and crowdfunded
        ideas that either get financed by reaching a minimum goal or not.
        Money will only be deducted from backers if the goal is reached. """

    max_duration = 120  # days

    def __init__(self, *args, **kwargs):
        # add the css and javascript files to project admin.
        super(Project, self).__init__(*args, **kwargs)
        self.feincms_item_editor_includes['head'].update([
            'admin/zipfelchappe/_project_head_include.html',
        ])

    title = models.CharField(_('title'), max_length=100)

    slug = models.SlugField(_('slug'), unique=True)

    position = models.IntegerField(_('ordering'))

    goal = CurrencyField(_('goal'), max_digits=10, decimal_places=2,
        help_text=_('Amount to be raised.'))

    currency = models.CharField(_('currency'), max_length=3,
        choices=CURRENCY_CHOICES, default=CURRENCY_CHOICES[0])

    start = models.DateTimeField(_('start'),
        help_text=_('Date when the project will be online.'))

    end = models.DateTimeField(_('end'),
        help_text=_('End of the fundraising campaign.'))

    backers = models.ManyToManyField('Backer', verbose_name=_('backers'),
        through='Pledge')

    teaser_image = models.ImageField(_('image'), blank=True, null=True,
        upload_to=teaser_img_upload_to)

    teaser_text = RichTextField(_('text'), blank=True)

    objects = ProjectManager()

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        ordering = ('position',)
        get_latest_by = 'end'

    def save(self, *args, **kwargs):
        model = self.__class__

        if self.position is None:
            try:
                last = model.objects.order_by('-position')[0]
                self.position = last.position + 1
            except IndexError:
                self.position = 0

        return super(Project, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    def clean(self):
        if self.start and self.end and self.start > self.end:
            raise ValidationError(_('Start must be before end'))

        if self.start and self.end and \
           self.end - self.start > timedelta(days=self.max_duration):
            raise ValidationError(_('Project duration can be max. %(duration) days'
                                    % {'duration': self.max_duration}))

        if self.pk:
            dbinst = Project.objects.get(pk=self.pk)

            if self.has_pledges and self.currency != dbinst.currency:
                raise ValidationError(_('You cannot change the currency anymore'
                    ' once your project has been backed by users'))

            if self.has_pledges and self.end != dbinst.end:
                raise ValidationError(_('You cannot change the end date anymore'
                    ' once your project has been backed by users'))

            if self.has_pledges and self.goal != dbinst.goal:
                raise ValidationError(_('You cannot change the goal '
                                        'once your project has been backed.'))

    @app_models.permalink
    def get_absolute_url(self):
        return 'zipfelchappe_project_detail', ROOT_URLS, (self.slug,)

    @classmethod
    def create_content_type(cls, model, *args, **kwargs):
        # Registers content type for translations too
        super(Project, cls).create_content_type(model, *args, **kwargs)
        if 'zipfelchappe.translations' in settings.INSTALLED_APPS:
            from .translations.models import ProjectTranslation
            kwargs['class_name'] = 'Translated%s' % model._meta.object_name
            ProjectTranslation.create_content_type(model, *args, **kwargs)

    @classmethod
    def register_regions(cls, *args, **kwargs):
        # Register regions for translations too
        super(Project, cls).register_regions(*args, **kwargs)
        if 'zipfelchappe.translations' in settings.INSTALLED_APPS:
            from .translations.models import ProjectTranslation
            ProjectTranslation.register_regions(*args, **kwargs)

    @cached_property
    def authorized_pledges(self):
        """
        Returns the Pledge instances which are autorized or paid.
        :return: Queryset of Pledges
        """
        return self.pledges.select_related('backer').filter(status__gte=Pledge.AUTHORIZED)

    @cached_property
    def collectable_pledges(self):
        """
        Returns the Pledge instances which are autorized but not paid.
        :return: Queryset of Pledges
        """
        return self.pledges.filter(status=Pledge.AUTHORIZED)

    @cached_property
    def has_pledges(self):
        return self.pledges.count() > 0

    @cached_property
    def achieved(self):
        """
        Returns the amount of money raised
        :return: Amount raised
        """
        amount = self.authorized_pledges.aggregate(Sum('amount'))
        return amount['amount__sum'] or 0

    @property
    def percent(self):
        return int(round((self.achieved * 100) / self.goal))

    @property
    def goal_display(self):  # TODO: localize
        return u'%s %s' % (int(self.goal), self.currency)

    @property
    def achieved_display(self):
        return u'%d %s (%d%%)' % (self.achieved, self.currency, self.percent)

    @property
    def is_active(self):
        return self.start < now() < self.end

    @property
    def is_over(self):
        return now() > self.end

    @property
    def less_than_24_hours(self):
        warnings.warn('This property is deprecated and will be removed.', DeprecationWarning, stacklevel=2)
        return self.end - now() < timedelta(hours=24)

    @property
    def is_financed(self):
        return self.achieved >= self.goal

    @property
    def ended_successfully(self):
        return self.is_financed and self.is_over

    @cached_property
    def update_count(self):
        return self.updates.filter(status='published').count()

    @cached_property
    def public_pledges(self):
        return self.pledges.select_related('backer').filter(
            status__gte=Pledge.AUTHORIZED,
            anonymously=False
        )

    def poster_image(self):
        return self.teaser_image if self.teaser_image else {'url': DEFAULT_IMAGE_URL}

    def extraform(self):
        """ Returns additional form required to pledge to this project """
        fields = SortedDict()

        for field in self.extrafields.all():
            field.add_formfield(fields, self)

        return type(b'Form%s' % self.pk, (forms.Form,), fields)


signals.post_syncdb.connect(check_db_schema(Project, __name__), weak=False)
