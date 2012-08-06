import re

from django import template
from django.utils.encoding import force_unicode
from django.utils.formats import number_format

register = template.Library()

@register.filter(is_safe=True)
def tickmark(value):
    orig = force_unicode(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>\'\g<2>', orig)
    if orig == new:
        return new
    else:
        return tickmark(new)
