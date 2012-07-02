from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
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

class ContentTypeMixin(models.Model):
    """
    Simplify some of the needed boilerplate code for objects which can
    have a foreign key to any other object.
    """

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    class Meta:
        abstract = True
