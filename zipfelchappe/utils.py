from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.fields import FieldDoesNotExist
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from .app_settings import (
    USER_EMAIL_FIELD, USER_FIRST_NAME_FIELD, USER_LAST_NAME_FIELD
)


# Not available in django 1.4 yet
def format_html(format_string, *args, **kwargs):
    """
    Similar to str.format, but passes all arguments through conditional_escape,
    and calls 'mark_safe' on the result. This function should be used instead
    of str.format or % interpolation to build up small HTML fragments.
    """
    args_safe = map(conditional_escape, args)
    kwargs_safe = dict([(k, conditional_escape(v)) for (k, v) in
                        kwargs.iteritems()])
    return mark_safe(format_string.format(*args_safe, **kwargs_safe))


def get_object_or_none(klass, *args, **kwargs):
    """
    Modelled after get_object_or_404
    """

    if isinstance(klass, models.query.QuerySet):
        queryset = klass
    elif isinstance(klass, models.manager.Manager):
        queryset = klass.all()
    else:
        queryset = klass._default_manager.all()

    try:
        return queryset.get(*args, **kwargs)
    except (queryset.model.DoesNotExist, ValueError):
        return None


def get_user_search_fields():
    ''' Get names of searchable fields on user model

    Due to custom user models the search_fields values for fields on the
    user model can't be set statically. This model returns the available
    fields on the model which can be used to dynamically generate
    search_fields values
    '''
    # get field names for user fields
    fields = [USER_EMAIL_FIELD, USER_FIRST_NAME_FIELD, USER_LAST_NAME_FIELD]

    # remove fields that don't exist on the model
    user_model = get_user_model()
    for field_name in fields[:]:
        try:
            user_model._meta.get_field_by_name(field_name)
        except FieldDoesNotExist:
            fields.remove(field_name)

    return fields
