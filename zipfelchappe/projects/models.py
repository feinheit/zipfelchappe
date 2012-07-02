from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from ..base import CreateUpdateModel
from ..fields import CurrencyField

class Project(CreateUpdateModel):

    created_by = models.ForeignKey(User, related_name='projects')
    title = models.CharField(_('title'), max_length=100)
    goal = CurrencyField(_('goal'), max_digits=10, decimal_places=2)
    
    description = models.TextField(_('description'), blank=True)
    
    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('project')

    def __unicode__(self):
        return self.title

