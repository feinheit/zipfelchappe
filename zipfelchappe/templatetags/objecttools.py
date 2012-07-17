from django import template

register = template.Library()

@register.filter
def attr(obj, attr):
    return getattr(obj, attr, None)
