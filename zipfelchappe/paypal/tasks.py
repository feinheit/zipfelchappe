import json

from zipfelchappe.models import Project, Pledge

from .models import Preapproval, Payment
from .paypal_api import create_payment


class PaypalException(Exception):
    pass


def process_pledge(pledge):
    """ 
    Collect the paypal payment of one pledge
    
    Payments are asynchronous and we'll get notified about payment status by 
    paypal via IPN Messages.
    """
    
    try:
        preapproval = pledge.paypal_preapproval
    except Preapproval.DoesNotExist:
        raise PaypalException('No preapproval for this pledge found')

    # All seems ok, try to execute paypal payment
    pp_payment = create_payment(preapproval)
    pp_data = pp_payment.json()

    Payment.objects.create(
        key=pp_data.get('payKey', 'ERROR_%s' % preapproval.key[:14]),
        preapproval=preapproval,
        status=pp_data.get('paymentExecStatus', 'ERROR'),
        data=json.dumps(pp_data, indent=2),
    )

    if pp_data and 'error' in pp_data:
        # Mark pledge as FAILED after 3 retries
        if preapproval.payments.count() >= 3:
            pledge.status = Pledge.FAILED
            pledge.save()
        for error in pp_data['error']:
            raise PaypalException(error['message'])
    
    return pp_data
    

def process_payments():
    """
    Collects the paypal payments for all successfully financed projects
    that end within the next 24 hours.
    """

    billable_projects = Project.objects.billable()

    # Pledges that are ready to be payed
    processing_pledges = Pledge.objects.filter(
        project__in=billable_projects,
        provider='paypal',
        status=Pledge.AUTHORIZED,
        paypal_preapproval__status='ACTIVE',
        paypal_preapproval__approved=True,
    )

    for pledge in processing_pledges:
        try:
            process_pledge(pledge)
        except PaypalException as e:
            print e.message

    return processing_pledges.count()
