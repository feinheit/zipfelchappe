
from zipfelchappe.models import Project, Pledge

from .models import Payment
from .direct_link_api import request_payment, update_payment


class PostfinanceException(Exception):
    pass
    
    
def process_pledge(pledge):
    """ Collect postfinance payment for exactly one pledge """
    try:
        payment = pledge.postfinance_payment
    except Payment.DoesNotExist:
        raise PostfinanceException('Payment not found')
        
    if payment.STATUS != '5':
        raise PostfinanceException('Payment is not authorized')
        
    try:
        result = request_payment(payment.PAYID)
    except Exception as e:
        raise PostfinanceException(e.message)
        
    if 'STATUS' not in result or result['STATUS'] == '0':
        raise PostfinanceException('Incomplete or invalid status')
    else:
        payment.STATUS = result['STATUS']
        payment.save()
        
    return result


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

    for pledge in pledges:
        try:
            process_pledge(pledge)
        except PostfinanceException as e:
            print e.message

    return pledges.count()


def update_payments():
    """ Update the status of all pending payments """
    payments = Payment.objects.filter(STATUS='91')

    for payment in payments:
        result = update_payment(payment.PAYID)
        payment.STATUS = result['STATUS']
        if payment.STATUS == '9':
            payment.pledge.status = Pledge.PAID
            payment.pledge.save()
        payment.save()

    return payments.count()
