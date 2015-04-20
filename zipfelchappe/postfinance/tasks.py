from __future__ import unicode_literals, absolute_import
import logging

from zipfelchappe.models import Project, Pledge
from .models import Payment, STATUS_DICT
from .api.direct_link_v1 import request_payment, update_payment

logger = logging.getLogger('zipfelchappe.postfinance.ipn')


class PostfinanceException(Exception):
    def __init__(self, message, *args, **kwargs):
        logger.exception('Exception: %s' % message)
        super(PostfinanceException, self).__init__(message, *args, **kwargs)

    
def process_pledge(pledge):
    """ Collect postfinance payment for exactly one pledge """
    try:
        payment = pledge.postfinance_payment
    except Payment.DoesNotExist:
        raise PostfinanceException('Payment for pledge %s not found' % pledge.pk)

    if payment.STATUS == '91':
        # payment is in processing state, check status
        result = update_payment(payment.PAYID)
        if result['STATUS'] == '9':
            payment.STATUS = result['STATUS']
            payment.save()

            payment.pledge.status = Pledge.PAID
            payment.pledge.save()
            logger.info('Pledge {0} has been paid.'.format(pledge.pk))
            return result
        logger.debug('New status for pledge {0}: {1}:{2}'.format(
            pledge.pk, payment.STATUS, STATUS_DICT[payment.STATUS]
        ))

    elif payment.STATUS == '5':
        # Payment is authorized, request transaction
        try:
            result = request_payment(payment.PAYID)
        except Exception as e:
            raise PostfinanceException(e.message)

        if 'STATUS' not in result or result['STATUS'] == '0':
            raise PostfinanceException('Incomplete or invalid status')
        else:
            payment.STATUS = result['STATUS']
            payment.save()
            logger.info('Pledge {0} has been paid. Status:{1}'.format(pledge.pk, result['STATUS']))

        return result
    else:
        raise PostfinanceException('Payment is not authorized')


def process_payments():
    """
    Collect postfinance payments for all successfully financed projects
    that end within the next 24 hours. Postfinance Direct Link Option is
    required for this to work.
    """

    billable_projects = Project.objects.billable()

    pledges = Pledge.objects.filter(
        project__in=billable_projects,
        provider='postfinance',
        status=Pledge.AUTHORIZED
    )
    logger.info('Collecting payments for {0} pledges in {1} projects.'.format(
        len(pledges), len(billable_projects)
    ))

    for pledge in pledges:
        try:
            process_pledge(pledge)
        except PostfinanceException as e:
            print e.message

    return pledges.count()


