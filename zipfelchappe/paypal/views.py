import logging
import json
import traceback

from django.http import HttpResponse, QueryDict
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from zipfelchappe.views import requires_pledge
from zipfelchappe.models import Pledge

from .models import Preapproval, Payment
from . import paypal_api

logger = logging.getLogger('zipfelchappe.paypal.ipn')

class PreapprovedAmountException(Exception):
    pass

@csrf_exempt
def ipn(request):

    try:
        logger.info("\nIPN RECEIVED:")

        data = request.POST.copy()
        data_json = json.dumps(data, ensure_ascii=False, indent=2)

        # Verify message if no exceptions raised
        if not paypal_api.verify_ipn_message(data):
            logger.warning('IPN not verified: %s' % data_json)
            return

        data['as_json'] = data_json

        if 'transaction_type' not in data:
            logger.warning('NO TRANSACTION TYPE: %s' % data['as_json'])
        elif data['transaction_type'] == 'Adaptive Payment PREAPPROVAL':
            handle_preapproval_ipn(request, data)
        elif data['transaction_type'] == 'Adaptive Payment PAY':
            handle_payment_ipn(request, data)
        else:
            logger.warning('UNHANDLED IPN MESSAGE: %s' % data['as_json'])

        return HttpResponse("Ok")
    except Exception, e:
        logger.error(traceback.format_exc())
        raise

def handle_preapproval_ipn(request, data):
    key = data['preapproval_key']

    try:
        p = Preapproval.objects.get(key=key)
        p.status = data['status']
        p.approved = data['approved'] == 'true'
        p.sender = data['sender_email']
        p.data = data['as_json']
        p.save()

        pledge = p.pledge
        if p.status == 'ACTIVE' and p.approved:
            pledge.status = Pledge.AUTHORIZED
        else:
            pledge.status = Pledge.UNAUTHORIZED
        pledge.save()

        logger.info('Preapproval message handled succefully')
    except Preapproval.DoesNotExist:
        logger.error('Prepapproval with key %s not found' % key)

def handle_payment_ipn(request, data):
    key = data['pay_key']

    try:
        p = Payment.objects.get(key=key)
        p.status = data['status']
        p.data = data['as_json']

        pledge = p.preapproval.pledge
        if p.status == 'COMPLETED':
            pledge.status = Pledge.PAID

        pledge.save()

        logger.info('Payment message handled succefully')
    except Payment.DoesNotExist:
        logger.error('Payment with key %s not found' % key)

@requires_pledge
def payment(request, pledge):
    try:
        preapproval = pledge.preapproval

        if preapproval.amount != pledge.amount:
            preapproval.delete()
            raise PreapprovedAmountException

    except (Preapproval.DoesNotExist, PreapprovedAmountException):
        r = paypal_api.create_preapproval(pledge)

        if 'preapprovalKey' in r.json:
            preapproval = Preapproval.objects.create(
                pledge = pledge,
                key = r.json['preapprovalKey'],
                amount = pledge.amount,
            )
        else:
            errormessages = []

            if 'error' in r.json:
                errormessages = [e['message'] for e in r.json['error']]

            return render(request, 'zipfelchappe/paypal/payment_error.html',  {
                'errormessages': errormessages,
                'pp_response': json.dumps(r.json, indent=2),
                'pledge': pledge,
                'project': pledge.project
            })

    parameters = QueryDict('cmd=_ap-preapproval&preapprovalkey=%s' % preapproval.key)
    return paypal_api.paypal_redirect(parameters)
