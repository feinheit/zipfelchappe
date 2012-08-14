from django.db import models
from django.utils.translation import ugettext_lazy as _


class CreateUpdateModel(models.Model):
    """
    Store timestamps for creation and last modification.
    """

    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True
        get_latest_by = 'created'
        ordering = ('created',)
