from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import signals, Q, Sum
from django.utils.translation import ugettext_lazy as _

from feincms.management.checker import check_database_schema as check_db_schema
from feincms.models import Base

from zipfelchappe import settings
from zipfelchappe.base import CreateUpdateModel
from zipfelchappe.fields import CurrencyField

CURRENCY_CHOICES = list(((cur, cur) for cur in settings.CURRENCIES))


class Payment(CreateUpdateModel):

    user = models.ForeignKey(User)

    project = models.ForeignKey('Project')

    amount = CurrencyField(_('amount'), max_digits=10, decimal_places=2)

    currency = models.CharField(_('currency'), max_length=3,
        choices=CURRENCY_CHOICES, editable=False)

    reward = models.ForeignKey('Reward', blank=True, null=True,
        related_name = 'payments')

    anonymously = models.BooleanField(_('anonymously'))

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __unicode__(self):
        return u'Payment of %d %s from %s to %s' % \
            (self.amount, self.currency, self.user, self.project)

    def save(self, *args, **kwargs):
        self.currency = self.project.currency
        super(Payment, self).save(*args, **kwargs)


class Reward(CreateUpdateModel):

    project = models.ForeignKey('Project', related_name='rewards')

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
        return u'Reward %d for %s' % (self.minimum, self.project)

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


class Project(Base):

    title = models.CharField(_('title'), max_length=100)

    slug = models.SlugField(_('slug'))

    goal = CurrencyField(_('goal'), max_digits=10, decimal_places=2,
        help_text = _('CHF you want to raise'))

    currency = models.CharField(_('currency'), max_length=3,
        choices=CURRENCY_CHOICES, default=CURRENCY_CHOICES[0])

    start = models.DateField(_('start'),
        help_text=_('Date the project will be online'))

    end = models.DateField(_('end'),
        help_text=_('Until when money is raised'))

    backers = models.ManyToManyField(User, through='Payment')

    def teaser_img_upload_to(instance, filename):
        return (u'projects/%s/%s' % (instance.slug, filename)).lower()

    teaser_image = models.ImageField(_('teaser_image'), blank=True, null=True,
        upload_to = teaser_img_upload_to)

    teaser_text = models.TextField(_('teaser text'), blank=True)


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
