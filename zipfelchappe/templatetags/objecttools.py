from django import template

register = template.Library()

@register.filter
def attr(obj, attribute):
    return getattr(obj, attribute, None)
