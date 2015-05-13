# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from ..payment_provider import BasePaymentProvider
from .tasks import process_pledge
from .app_settings import MAXIMUM_ALLOWED_REWARD


class PaypalProvider(BasePaymentProvider):
    """
    The Payment Provider Postfinance.
    """
    def __unicode__(self):
        return 'Paypal'

    def payment_url(self):
        return reverse('zipfelchappe_paypal_payment')

    def collect_pledge(self, pledge):
        return process_pledge(pledge)

    def validate_project(self, project, db_instance=None):
        """
        A provider can validate a project.
        :param project: The project instance to validate
        :param db_instance: The project instance in the database
        :raise: ValidationError
        """
        rewards = project.rewards.all()
        if len(rewards) > 0:
            for reward in rewards:
                if reward.minimum > MAXIMUM_ALLOWED_REWARD:
                    raise ValidationError(_('A reward cannot exceed the amount of US$ %(amount)s. '
                                            'Please consult the PayPal Crowdfunding Application '
                                            'Guidelines.' % {'amount': MAXIMUM_ALLOWED_REWARD}))

        if db_instance:
            if project.has_pledges and project.end != db_instance.end:
                raise ValidationError(_('You cannot change the end date anymore'
                                        ' once your project has been backed by users'))

            if project.has_pledges and project.goal != db_instance.goal:
                raise ValidationError(_('You cannot change the goal '
                                        'once your project has been backed.'))

