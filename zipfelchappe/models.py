from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals, Q
from django.utils.translation import ugettext_lazy as _

from feincms.management.checker import check_database_schema as check_db_schema
from feincms.models import Base

from zipfelchappe.base import CreateUpdateModel
from zipfelchappe.fields import CurrencyField


class Project(Base):

    title = models.CharField(_('title'), max_length=100)

    slug = models.SlugField(_('slug'))

    goal = CurrencyField(_('goal'), max_digits=10, decimal_places=2,
        help_text = _('CHF you want to raise'))

    start = models.DateField(_('start'),
        help_text=_('Date the project will be online'))

    end = models.DateField(_('end'),
        help_text=_('Until when money is raised'))

    payments = models.ManyToManyField(User, through='Payment')

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        get_latest_by = 'end'


    def __unicode__(self):
        return self.title

signals.post_syncdb.connect(check_db_schema(Project, __name__), weak=False)


class Reward(CreateUpdateModel):

    project = models.ForeignKey(Project, related_name='rewards')

    order = models.PositiveIntegerField(default=1)

    minimum = CurrencyField(_('minimum'), max_digits=10, decimal_places=2,
        help_text = _('How much does one have to donate to receive this?'))

    description = models.TextField(_('description'), blank=True)

    quantity = models.IntegerField(_('quantity'), blank=True, null=True,
        help_text = _('How many times can this award be give away? Leave empty \
                       to means unlimited'))

    class Meta:
        verbose_name = _('reward')
        verbose_name_plural = _('rewards')

    def __unicode__(self):
        return u'Reward %d for %s' % (self.minimum, self.project)

class Payment(CreateUpdateModel):

    user = models.ForeignKey(User)

    project = models.ForeignKey(Project)

    amount = CurrencyField(_('amount'), max_digits=10, decimal_places=2)

    reward = models.ForeignKey(Reward, blank=True, null=True)

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __unicode__(self):
        return u'Payment of %d CHF from %s to %s' % \
            (self.amount, self.user, self.project)