from django.conf import settings
from django import template

register = template.Library()

if 'django.contrib.comments' in settings.INSTALLED_APPS:
    from django.contrib.comments.templatetags.comments import *
else:
    @register.simple_tag(name='get_comment_count')
    @register.simple_tag(name='get_comment_list')
    @register.simple_tag(name='render_comment_list')
    @register.simple_tag(name='get_comment_form')
    @register.simple_tag(name='render_comment_form')
    @register.simple_tag(name='comment_form_target')
    @register.simple_tag(name='get_comment_permalink')
    def empty_tag(*args, **kwargs):
        return None
