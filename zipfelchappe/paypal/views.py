from pytz import utc
from datetime import datetime
import logging
import requests
import json

from django.http import HttpResponse, QueryDict
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.contrib.sites.models import get_current_site
from django.utils.translation import get_language, to_locale

from zipfelchappe.views import requires_pledge

from .import app_settings as settings

logger = logging.getLogger('zipfelchappe.paypal.ipn')


pp_req_headers = {
    'X-PAYPAL-SECURITY-USERID': settings.PAYPAL_USERID,
    'X-PAYPAL-SECURITY-PASSWORD': settings.PAYPAL_PASSWORD,
    'X-PAYPAL-SECURITY-SIGNATURE': settings.PAYPAL_SIGNATURE,
    'X-PAYPAL-REQUEST-DATA-FORMAT': 'JSON',
    'X-PAYPAL-RESPONSE-DATA-FORMAT': 'JSON'
}

def zuluTimeFormat(date):
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')

def paypal_redirect(params):
    if settings.PAYPAL_LIVE:
        pp_url = 'https://paypal.com/en/webscr?%s' % params.urlencode()
    else:
        pp_url = 'https://sandbox.paypal.com/en/webscr?%s' % params.urlencode()

    print pp_url

    return redirect(pp_url)

@csrf_exempt
def ipn(request):
    request.encoding = 'windows-1252'

    try:
        parameters = request.POST.copy()
        parameters_repr = repr(parameters).encode('utf-8')

        logger.info("\nIPN RECEIVED:")

        if parameters:
            for k, v in parameters.iteritems():
                logger.info("%s: %s" %(k, v.encode('windows-1252')))

        return HttpResponse("Ok")

    except Exception, e:
        return HttpResponse('Failure')
        raise

@requires_pledge
def payment(request, pledge):

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
        'maxAmountPerPayment': unicode(pledge.amount),
        'maxTotalAmountOfAllPayments': unicode(pledge.amount),
        'startingDate': zuluTimeFormat(datetime.utcnow()),
        'endingDate': zuluTimeFormat(pledge.project.end),
        'memo': pledge.project.title,
        'pinType': 'NOT_REQUIRED',
        "requestEnvelope": {'errorLanguage' : 'en_US'},
    }

    r = requests.post(url, headers=pp_req_headers, data=json.dumps(data))

    if 'preapprovalKey' in r.json:
        key = r.json['preapprovalKey']
        parameters = QueryDict('cmd=_ap-preapproval&preapprovalkey=%s' % key)
        return paypal_redirect(parameters)
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

@requires_pledge
def thankyou(request, pledge):
    return render(request, 'zipfelchappe/paypal/thankyou.html')


@requires_pledge
def canceled(request, pledge):
    return render(request, 'zipfelchappe/paypal/canceled.html')
