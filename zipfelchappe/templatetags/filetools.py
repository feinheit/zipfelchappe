from os.path import basename
from mimetypes import guess_type

from django import template
from django.utils.encoding import force_unicode

register = template.Library()

@register.filter
def filename(name):
    return basename(force_unicode(name))

@register.filter
def mimetype(name):
    return guess_type(force_unicode(name))[0]
