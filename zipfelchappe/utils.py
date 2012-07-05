
from django.db import models
from django.core.exceptions import ImproperlyConfigured

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
