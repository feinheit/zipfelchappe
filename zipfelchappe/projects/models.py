from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from ..base import CreateUpdateModel
from ..fields import CurrencyField

class Project(CreateUpdateModel):

    created_by = models.ForeignKey(User, related_name='projects')

    title = models.CharField(_('title'), max_length=100)

    goal = CurrencyField(_('goal'), max_digits=10, decimal_places=2,
        help_text = _('CHF you want to raise'))

    start = models.DateField(_('end'),
        help_text=_('Date the project will be online'))

    end = models.DateField(_('end'),
        help_text=_('Until when should money be raised'))

    description = models.TextField(_('description'), blank=True)

    website = models.URLField(_('website'), blank=True, null=True)

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('project')

    def __unicode__(self):
        return self.title

class Reward(CreateUpdateModel):

    project = models.ForeignKey(Project, related_name='rewards')

    order = models.PositiveIntegerField(default=1)

    minimum = CurrencyField(_('limit'), max_digits=10, decimal_places=2,
        help_text = _('How much does one have to donate to receive this?'))

    description = models.TextField(_('description'), blank=True)

    quantity = models.IntegerField(_('quantity'), blank=True, null=True,
        help_text = _('How many times can this award be give away? Leave empty \
                       to means unlimited'))
