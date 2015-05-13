# coding: utf-8
from __future__ import absolute_import, unicode_literals
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from ..payment_provider import BasePaymentProvider
from .tasks import process_pledge
from .app_settings import MAX_BLOCKING_DURATION_DAYS


class PostfinanceProvider(BasePaymentProvider):
    """
    The Payment Provider Postfinance.
    """
    def __unicode__(self):
        return 'Postfinance'

    def payment_url(self):
        return reverse('zipfelchappe_postfinance_payment')

    def collect_pledge(self, pledge):
        return process_pledge(pledge)

    def validate_project(self, project, db_instance=None):
        """
        A provider can validate a project.
        :param project: The project instance to validate
        :param db_instance: The project instance in the database
        :raise: ValidationError
        """
        if project.start and project.end and \
           project.end - project.start > timedelta(days=MAX_BLOCKING_DURATION_DAYS):
            raise ValidationError(_('Project duration can be max. %(duration) '
                                    'days because of Postfinance rules.'
                                    % {'duration': MAX_BLOCKING_DURATION_DAYS}))

