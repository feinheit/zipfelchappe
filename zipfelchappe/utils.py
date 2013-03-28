
from django.conf import settings
from django.db import models
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


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