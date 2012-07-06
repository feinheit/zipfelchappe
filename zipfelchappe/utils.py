
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe

from . import app_settings

def get_backer_model():
    if not hasattr(get_backer_model, '_cached_model'):
        try:
            app_label, model_name = app_settings.BACKER_MODEL.split('.')
        except ValueError:
            raise ImproperlyConfigured( 'app_label and model_name should be ' +
                'separated by a dot in the ZIPFELCHAPPE_BACKER_MODEL setting')
        try:
            model = models.get_model(app_label, model_name)
            if model is None:
                raise ImproperlyConfigured('Unable to load the backer model, ' +
                    'check ZIPFELCHAPPE_BACKER_MODEL in your project settings')
            get_backer_model._cached_model = model
        except (ImportError):
            raise

    return get_backer_model._cached_model

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
