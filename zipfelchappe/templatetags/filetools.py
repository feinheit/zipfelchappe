from os.path import basename
from mimetypes import guess_type

from django import template
from django.utils.encoding import force_unicode

register = template.Library()

@register.filter
def filename(filename):
    return basename(force_unicode(filename))

@register.filter
def mimetype(filename):
    return guess_type(force_unicode(filename))[0]
