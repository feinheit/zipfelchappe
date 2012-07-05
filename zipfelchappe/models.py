import datetime
from dateutil import relativedelta

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.db import models
from django.db.models import signals, Q, Sum
from django.utils.translation import ugettext_lazy as _

from feincms.models import Base
from feincms.management.checker import check_database_schema as check_db_schema

from . import app_settings
from .base import CreateUpdateModel
from .fields import CurrencyField

if app_settings.BACKER_MODEL:
    BACKER_MODEL = app_settings.BACKER_MODEL
else:
    raise ImproperlyConfigured('You need to set ZIPFELCHAPPE_BACKER_MODEL' +
        'in your project settings')

CURRENCY_CHOICES = list(((cur, cur) for cur in app_settings.CURRENCIES))

class BackerModel(models.Model):

    user = models.ForeignKey(User, blank=True, null=True)

    first_name = models.CharField(_('first name'), max_length=30, blank=True,
        help_text=_('Cannot be change if a user is selected'))

    last_name = models.CharField(_('last name'), max_length=30, blank=True,
        help_text=_('Cannot be change if a user is selected'))

    email = models.EmailField(_('e-mail address'), blank=True,
        help_text=_('Cannot be change if a user is selected'))

    class Meta:
        verbose_name = _('backer')
        verbose_name_plural = _('backers')
        abstract = True

    def __unicode__(self):
        return u"%s" % self.user.get_full_name()

    def save(self, *args, **kwargs):
        if self.user:
            self.first_name = self.user.first_name
            self.last_name = self.user.last_name
            self.email = self.user.email
        super(BackerModel, self).save(*args, **kwargs)

if app_settings.BACKER_MODEL == 'zipfelchappe.DefaultBacker':
    class DefaultBacker(BackerModel):
        pass

class Payment(CreateUpdateModel):

    backer = models.ForeignKey(BACKER_MODEL, verbose_name=_('backer'),
        related_name='payments')

    project = models.ForeignKey('Project', verbose_name=_('project'),
        related_name='payments')

    amount = CurrencyField(_('amount'), max_digits=10, decimal_places=2)

    currency = models.CharField(_('currency'), max_length=3,
        choices=CURRENCY_CHOICES, editable=False, default=CURRENCY_CHOICES[0])

    reward = models.ForeignKey('Reward', blank=True, null=True,
        related_name = 'payments')

    anonymously = models.BooleanField(_('anonymously'))

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __unicode__(self):
        return u'Payment of %d %s from %s to %s' % \
            (self.amount, self.currency, self.backer, self.project)

    def save(self, *args, **kwargs):
        self.currency = self.project.currency
        super(Payment, self).save(*args, **kwargs)


class Reward(CreateUpdateModel):

    project = models.ForeignKey('Project', verbose_name=_('project'),
        related_name='rewards')

    title = models.CharField(_('title'), max_length=100)

    minimum = CurrencyField(_('minimum'), max_digits=10, decimal_places=2,
        help_text = _('How much does one have to donate to receive this?'))

    description = models.TextField(_('description'), blank=True)

    quantity = models.IntegerField(_('quantity'), blank=True, null=True,
        help_text = _('How many times can this award be give away? Leave ' +
                      'empty to means unlimited'))

    class Meta:
        verbose_name = _('reward')
        verbose_name_plural = _('rewards')
        ordering = ['minimum',]

    def __unicode__(self):
        return self.title

    def clean(self):
        if self.quantity != None and self.quantity < self.awarded:
            raise ValidationError(_('Cannot reduce quantiy to a lower value ' +
                'than it was allready promised to backers'))

    @property
    def awarded(self):
        return self.payments.count()

    @property
    def available(self):
        return self.quantity - self.awarded


class Category(CreateUpdateModel):

    title = models.CharField(_('title'), max_length=100)

    slug = models.SlugField(_('slug'), unique=True)

    ordering = models.SmallIntegerField(_('ordering'), default=0)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['ordering']

    def __unicode__(self):
        return self.title


class Project(Base):

    title = models.CharField(_('title'), max_length=100)

    slug = models.SlugField(_('slug'), unique=True)

    goal = CurrencyField(_('goal'), max_digits=10, decimal_places=2,
        help_text = _('Amount you want to raise'))

    currency = models.CharField(_('currency'), max_length=3,
        choices=CURRENCY_CHOICES, default=CURRENCY_CHOICES[0])

    start = models.DateField(_('start'),
        help_text=_('Date the project will be online'))

    end = models.DateField(_('end'),
        help_text=_('Until when money is raised'))

    categories = models.ManyToManyField(Category, verbose_name=_('categories'),
        related_name='projects', null=True, blank=True)

    backers = models.ManyToManyField(BACKER_MODEL, verbose_name=_('backers'),
        through='Payment')

    def teaser_img_upload_to(instance, filename):
        return (u'projects/%s/%s' % (instance.slug, filename)).lower()

    teaser_image = models.ImageField(_('image'), blank=True, null=True,
        upload_to = teaser_img_upload_to)

    teaser_text = models.TextField(_('text'), blank=True)


    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        get_latest_by = 'end'


    def __unicode__(self):
        return self.title

    def clean(self):
        if self.start > self.end:
            raise ValidationError(_('Start must be before end'))

        if self.pk:
            dbinst = Project.objects.get(pk=self.pk)

            if dbinst.has_payments and self.currency != dbinst.currency:
                raise ValidationError(_('Cannot change currency with payments!'))


    @property
    def payments(self):
        return Payment.objects.filter(project=self)

    @property
    def has_payments(self):
        return self.payments.count() > 0

    @property
    def achieved(self):
        return self.payments.aggregate(Sum('amount'))['amount__sum']

    @property
    def percent(self):
        return (self.achieved * 100) / self.goal


signals.post_syncdb.connect(check_db_schema(Project, __name__), weak=False)
