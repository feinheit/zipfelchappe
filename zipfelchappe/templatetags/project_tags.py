from datetime import timedelta

from django.utils import timezone
from django import template

register = template.Library()

@register.filter
def status_class(project):
    if project is None:
        return ''
    elif project.is_active and not project.is_financed:
        return 'active'
    elif project.is_active and project.is_financed:
        return 'active funded'
    elif project.is_financed:
        return 'finished successfully'
    else:
        return 'finished unsuccessfully'

@register.filter
def bar_class(project):
    if project is None:
        return ''
    elif not project.is_active and not project.is_financed:
        return 'warning'
    elif project.is_financed:
        return 'success'
    else:
        return 'info'

@register.filter
def remaining(project, value):
    if project and project.is_active:
        td = project.end - timezone.now()
        if value == 'days':
            return td.days
        elif value == 'hours':
            return td.seconds//3600
        elif value == 'minutes':
            return (td.seconds//60)%60
    else:
        return 0
