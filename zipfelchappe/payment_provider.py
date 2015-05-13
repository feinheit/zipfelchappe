# coding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

# https://charlesleifer.com/blog/django-patterns-pluggable-backends/
from . import PaymentProviderException

logger = logging.getLogger(__name__)


class BasePaymentProvider(object):
    """
    The abstract base class for all payment providers.
    """
    def __init__(self, name):
        self.name = name

    def __unicode__(self):
        return 'Base payment provider'

    def payment_url(self):
        """
        :return: The payment URL
        """
        raise NotImplementedError()

    def validate_project(self, project, db_instance=None):
        """
        A provider can validate a project.
        :param project: The project instance to validate
        :param db_instance: The project instance in the database
        :raise: ValidationError
        """
        pass

    def collect_pledge(self, pledge):
        """
        Collects payment for the given pledge.
        :param pledge: An authorized pledge.
        """
        raise NotImplementedError()

    def refund_pledge(self, pledge):
        """
        Frees reserved funds for the given pledge.
        :param pledge: An authorized pledge.
        """
        raise NotImplementedError()

    def collect_billable_payments(self, project):
        """
        Collects billable payments for the given project.
        :param project: The project to collect payments for.
        :return: The amount of processed pledges.
        """
        pledges = project.authorized_pledges.filter(provider=self.name)
        for pledge in pledges:
            try:
                self.collect_pledge(pledge)
            except PaymentProviderException as e:
                logger.info(e.message)

    def refund_payments(self, project):
        """
        Refunds reserved payments for the given project.
        :param project: The project to collect payments for.
        :return: The amount of processed pledges.
        """
        raise NotImplementedError()

