from pytz import utc
from datetime import datetime
import logging
import requests
import json
import traceback

from django.http import HttpResponse, QueryDict
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.contrib.sites.models import get_current_site
from django.utils.translation import get_language, to_locale

from zipfelchappe.views import requires_pledge
from zipfelchappe.models import Pledge

from .import app_settings as settings
from .models import Preapproval

logger = logging.getLogger('zipfelchappe.paypal.ipn')

class PreapprovedAmountException(Exception):
    pass

pp_req_headers = {
    'X-PAYPAL-SECURITY-USERID': settings.PAYPAL_USERID,
    'X-PAYPAL-SECURITY-PASSWORD': settings.PAYPAL_PASSWORD,
    'X-PAYPAL-SECURITY-SIGNATURE': settings.PAYPAL_SIGNATURE,
    'X-PAYPAL-REQUEST-DATA-FORMAT': 'JSON',
    'X-PAYPAL-RESPONSE-DATA-FORMAT': 'JSON'
}

PP_LIVE_URL = 'https://www.paypal.com/en/webscr'
PP_SANDBOX_URL = 'https://www.sandbox.paypal.com/en/webscr'

PP_URL = PP_LIVE_URL if settings.PAYPAL_LIVE else PP_SANDBOX_URL

def zuluTimeFormat(date):
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')

def paypal_redirect(params):
    return redirect('%s?%s' % (PP_URL, params.urlencode()))

@csrf_exempt
def ipn(request):

    try:
        logger.info("\nIPN RECEIVED:")

        data = request.POST.copy()
        data_json = json.dumps(data, ensure_ascii=False, indent=2)

        # Verify message if no exceptions raised
        verify_params = {'cmd': '_notify-validate'}
        verify_params.update(data)
        verify = requests.post(PP_URL, params=verify_params)

        if verify.text != 'VERIFIED':
            logger.warning('IPN not verified: %s' % data_json)
            return

        logger.info('Verify result: %s' % verify.text)

        data['as_json'] = data_json

        if 'transaction_type' not in data:
            logger.warning('NO TRANSACTION TYPE: %s' % data['as_json'])
        elif data['transaction_type'] == 'Adaptive Payment PREAPPROVAL':
            handle_preapproval_ipn(request, data)
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



@requires_pledge
def payment(request, pledge):

    try:
        preapproval = pledge.preapproval

        if preapproval.amount != pledge.amount:
            preapproval.delete()
            raise PreapprovedAmountException

    except (Preapproval.DoesNotExist, PreapprovedAmountException):
        site = get_current_site(request)
        url = 'https://svcs.sandbox.paypal.com/AdaptivePayments/Preapproval'
        data = {
            'returnUrl': 'http://%s%s' %
                (site, reverse('zipfelchappe_paypal_thankyou')),
            'cancelUrl': 'http://%s%s' %
                (site, reverse('zipfelchappe_paypal_canceled')),
            'ipnNotificationUrl': 'http://%s%s' %
                (site, reverse('zipfelchappe_paypal_ipn')),
            'currencyCode': pledge.currency,
            'maxNumberOfPayments': 1,
            'maxTotalAmountOfAllPayments': unicode(pledge.amount),
            'displayMaxTotalAmount': True,
            'startingDate': zuluTimeFormat(datetime.utcnow()),
            'endingDate': zuluTimeFormat(pledge.project.end),
            'memo': pledge.project.title,
            'pinType': 'NOT_REQUIRED',
            "requestEnvelope": {'errorLanguage' : 'en_US'},
        }

        r = requests.post(url, headers=pp_req_headers, data=json.dumps(data))

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
                'req_data': json.dumps(data, indent=2),
                'pledge': pledge,
                'project': pledge.project
            })

    parameters = QueryDict('cmd=_ap-preapproval&preapprovalkey=%s' % preapproval.key)
    return paypal_redirect(parameters)

@requires_pledge
def thankyou(request, pledge):
    if pledge.status == Pledge.AUTHORIZED:
        del request.session['pledge_id']
    return render(request, 'zipfelchappe/paypal/thankyou.html')


@requires_pledge
def canceled(request, pledge):
    return render(request, 'zipfelchappe/paypal/canceled.html')
