from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from django.db import models
from django.db.models import signals, Sum

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language
from django.utils.timezone import now

from feincms.models import Base
from feincms.management.checker import check_database_schema as check_db_schema
from feincms.utils.queryset_transform import TransformQuerySet
from feincms.content.application import models as app_models

from .app_settings import CURRENCIES, PAYMENT_PROVIDERS
from .base import CreateUpdateModel
from .fields import CurrencyField

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
            except:
                self._translation = self

            return self._translation


class Backer(models.Model):
    """ The base model for all project backers with some transient attributes
        to overwrite user attributes. This is only necessary to support offline
        pledges that were not created on the platform itself. """

    user = models.ForeignKey(User, blank=True, null=True, unique=True)

    _first_name = models.CharField(_('first name'), max_length=30, blank=True)

    _last_name = models.CharField(_('last name'), max_length=30, blank=True)

    _email = models.EmailField(_('e-mail address'), blank=True)

    class Meta:
        verbose_name = _('backer')
        verbose_name_plural = _('backers')

    def __unicode__(self):
        return self.full_name

    @property
    def first_name(self):
        if self.user and self.user.first_name:
            return self.user.first_name
        else:
            return self._first_name

    @property
    def last_name(self):
        if self.user and self.user.last_name:
            return self.user.last_name
        else:
            return self._last_name

    @property
    def email(self):
        if self.user and self.user.email:
            return self.user.email
        else:
            return self._email

    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return u'%s %s' % (self.first_name, self.last_name)
        else:
            return unicode(self.user)


PAYMENT_PROVIDERS += (('offline', _('Offline')),)
DEFAULT_PAYMENT_PROVIDER = PAYMENT_PROVIDERS[0][0]


class Pledge(CreateUpdateModel, TranslatedMixin):
    """ The connection between a backer and a project. One pledge corresponds
        exactly with one payment for a project. The payment itself however is
        tracked in the provider implementation. Based on the outcoming of the
        payment process, the payment provider must change the pledge status. """

    UNAUTHORIZED = 10
    AUTHORIZED = 20
    PAID = 30
    FAILED = 40

    STATUS_CHOICES = (
        (UNAUTHORIZED, _('Unauthorized')),
        (AUTHORIZED, _('Authorized')),
        (PAID, _('Paid')),
        (FAILED, _('Failed')),
    )

    backer = models.ForeignKey('Backer', verbose_name=_('backer'),
        related_name='pledges', blank=True, null=True)

    project = models.ForeignKey('Project', verbose_name=_('project'),
        related_name='pledges')

    amount = CurrencyField(_('amount'), max_digits=10, decimal_places=2)

    currency = models.CharField(_('currency'), max_length=3,
        choices=CURRENCY_CHOICES, editable=False, default=CURRENCY_CHOICES[0])

    reward = models.ForeignKey('Reward', blank=True, null=True,
        related_name='pledges')

    anonymously = models.BooleanField(_('anonymously'),
        help_text=_('You will not appear in the backer list'))

    provider = models.CharField(_('payment provider'), max_length=20,
        choices=PAYMENT_PROVIDERS, default=DEFAULT_PAYMENT_PROVIDER)

    # The internal status of the pledge, common for all payment providers
    status = models.PositiveIntegerField(_('status'), choices=STATUS_CHOICES,
            default=UNAUTHORIZED)

    class Meta:
        verbose_name = _('pledge')
        verbose_name_plural = _('pledges')

    def __unicode__(self):
        return u'Pledge of %d %s from %s to %s' % \
            (self.amount, self.currency, self.backer, self.project)

    def save(self, *args, **kwargs):
        self.currency = self.project.currency
        super(Pledge, self).save(*args, **kwargs)


class Reward(CreateUpdateModel, TranslatedMixin):
    """ A reward is a give-away for backers that pledge a certain amount.
        Rewards may be limited to a maximum number of backers. """

    project = models.ForeignKey('Project', verbose_name=_('project'),
        related_name='rewards')

    minimum = CurrencyField(_('minimum'), max_digits=10, decimal_places=2,
        help_text=_('How much does one have to donate to receive this?'))

    description = models.TextField(_('description'), blank=True)

    quantity = models.IntegerField(_('quantity'), blank=True, null=True,
        help_text=_('How many times can this award be given away? Leave ' +
            'empty to means unlimited'))

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
        return self.pledges.count()

    @property
    def awarded(self):
        return self.pledges.filter(status__gte=Pledge.AUTHORIZED).count()

    @property
    def available(self):
        return self.quantity - self.awarded

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
        return ('zipfelchappe_project_category_list', 'zipfelchappe.urls',
             (self.slug,)
        )

    @property
    def project_count(self):
        return self.projects.count()


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
    mails_sent = models.BooleanField(editable=False)

    def update_upload_to(instance, filename):
        return (u'projects/%s/updates/%s' % (instance.project.slug, filename)).lower()

    image = models.ImageField(_('image'), blank=True, null=True,
        upload_to=update_upload_to)

    external = models.URLField(_('external content'), blank=True, null=True,
         help_text=_('Check http://embed.ly/providers for more details'),
    )

    content = models.TextField(_('content'), blank=True)

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
        return ('zipfelchappe_update_detail', 'zipfelchappe.urls',
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

    template = models.TextField(_('template'))

    class Meta:
        verbose_name = _('mail')
        verbose_name_plural = _('mails')
        unique_together = (('project', 'action'),)

    def __unicode__(self):
        return '%s mail for %s' % (self.action, self.project)


class ProjectManager(models.Manager):

    def get_query_set(self):
        return TransformQuerySet(self.model, using=self._db)

    def online(self):
        return self.filter(start__lte=now)

    def funding(self):
        return self.online().filter(end__gte=now)

    def billable(self):
        """ Returns a list of projects that are successfully financed
            and end within the next 24 hours (payments can be collected) """
        ending = self.filter(end__gte=now(), end__lte=now()+timedelta(days=1))
        return list([project for project in ending if project.is_financed])


class Project(Base, TranslatedMixin):
    """ The heart of zipfelchappe. Projects are time limited and crowdfunded
        ideas that either get financed by reaching a minimum goal or not.
        Money will only be deducted from backers if the goal is reached. """

    title = models.CharField(_('title'), max_length=100)

    slug = models.SlugField(_('slug'), unique=True)

    position = models.IntegerField('#')

    goal = CurrencyField(_('goal'), max_digits=10, decimal_places=2,
        help_text=_('Amount you want to raise'))

    currency = models.CharField(_('currency'), max_length=3,
        choices=CURRENCY_CHOICES, default=CURRENCY_CHOICES[0])

    start = models.DateTimeField(_('start'),
        help_text=_('Date the project will be online'))

    end = models.DateTimeField(_('end'),
        help_text=_('Until when money is raised'))

    backers = models.ManyToManyField('Backer', verbose_name=_('backers'),
        through='Pledge')

    def teaser_img_upload_to(instance, filename):
        return (u'projects/%s/%s' % (instance.slug, filename)).lower()

    teaser_image = models.ImageField(_('image'), blank=True, null=True,
        upload_to=teaser_img_upload_to)

    teaser_text = models.TextField(_('text'), blank=True)

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
           self.end - self.start > timedelta(days=120):
            raise ValidationError(_('Project length can be max. 120 days'))

        if self.pk:
            dbinst = Project.objects.get(pk=self.pk)

            if self.has_pledges and self.currency != dbinst.currency:
                raise ValidationError(_('You cannot change the currency anymore'
                    ' once your project has been backed by users'))

            if self.has_pledges and self.end != dbinst.end:
                raise ValidationError(_('You cannot change the end date anymore'
                    ' once your project has been backed by users'))

    @app_models.permalink
    def get_absolute_url(self):
        return ('zipfelchappe_project_detail', 'zipfelchappe.urls',
            (self.slug,)
        )

    @classmethod
    def create_content_type(cls, model, *args, **kwargs):
        # Registers content type for translations too
        super(Project, cls).create_content_type(model, *args, **kwargs)
        if 'zipfelchappe.translations' in settings.INSTALLED_APPS:
            from zipfelchappe.translations.models import ProjectTranslation
            kwargs['class_name'] = 'Translated%s' % model._meta.object_name
            ProjectTranslation.create_content_type(model, *args, **kwargs)

    @classmethod
    def register_regions(cls, *args, **kwargs):
        # Register regions for translations too
        super(Project, cls).register_regions(*args, **kwargs)
        if 'zipfelchappe.translations' in settings.INSTALLED_APPS:
            from zipfelchappe.translations.models import ProjectTranslation
            ProjectTranslation.register_regions(*args, **kwargs)

    @property
    def authorized_pledges(self):
        return self.pledges.filter(status__gte=Pledge.AUTHORIZED)

    @property
    def has_pledges(self):
        return self.pledges.count() > 0

    @property
    def achieved(self):
        amount = self.authorized_pledges.aggregate(Sum('amount'))
        return amount['amount__sum'] or 0

    @property
    def percent(self):
        return int((self.achieved * 100) / self.goal)

    @property
    def goal_display(self):
        return u'%s %s' % (int(self.goal), self.currency)

    @property
    def achieved_display(self):
        return u'%d %s (%d%%)' % (self.achieved, self.currency, self.percent)

    @property
    def is_active(self):
        return now() < self.end

    @property
    def less_than_24_hours(project):
        return project.end - now() < timedelta(hours=24)

    @property
    def is_financed(self):
        return self.achieved >= self.goal

    @property
    def update_count(self):
        return self.updates.filter(status='published').count()

    @property
    def public_pledges(self):
        return self.pledges.filter(
            status__gte=Pledge.AUTHORIZED,
            anonymously=False
        )

# Zipfelchappe has two fixed regions which cannot be configured a.t.m.
# This may change in future versions but suffices our needs for now
Project.register_regions(
    ('main', _('Content')),
    ('thankyou', _('Thank you')),
)

signals.post_syncdb.connect(check_db_schema(Project, __name__), weak=False)
