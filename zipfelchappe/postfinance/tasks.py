
from zipfelchappe.models import Project, Pledge

from .models import Payment
from .direct_link_api import request_payment, update_payment


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

    payments = Payment.objects.filter(
        pledge__in=pledges,
        STATUS='5'
    )

    for payment in payments:
        result = request_payment(payment.PAYID)
        payment.STATUS = result['STATUS']
        payment.save()

    return payments.count()


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
