import json
import requests
from datetime import datetime
from decimal import Decimal

from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.shortcuts import render, redirect

from feincms.content.application.models import app_reverse

from .import app_settings as settings

PP_REQ_HEADERS = {
    'X-PAYPAL-SECURITY-USERID': settings.PAYPAL_USERID,
    'X-PAYPAL-SECURITY-PASSWORD': settings.PAYPAL_PASSWORD,
    'X-PAYPAL-SECURITY-SIGNATURE': settings.PAYPAL_SIGNATURE,
    'X-PAYPAL-APPLICATION-ID': settings.PAYPAL_APPLICATIONID,
    'X-PAYPAL-REQUEST-DATA-FORMAT': 'JSON',
    'X-PAYPAL-RESPONSE-DATA-FORMAT': 'JSON'
}

PP_API_LIVE_URL = 'https://svcs.paypal.com'
PP_API_SANDBOX_URL = 'https://svcs.sandbox.paypal.com'

PP_CMD_LIVE_URL = 'https://www.paypal.com/en/webscr'
PP_CMD_SANDBOX_URL = 'https://www.sandbox.paypal.com/en/webscr'

PP_API_URL = PP_API_LIVE_URL if settings.PAYPAL_LIVE else PP_API_SANDBOX_URL
PP_CMD_URL = PP_CMD_LIVE_URL if settings.PAYPAL_LIVE else PP_CMD_SANDBOX_URL

def zuluTimeFormat(date):
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')


def paypal_redirect(params):
    return redirect('%s?%s' % (PP_CMD_URL, params.urlencode()))


def verify_ipn_message(data):
    verify_params = {'cmd': '_notify-validate'}
    verify_params.update(data)
    verify_result = requests.post(PP_CMD_URL, params=verify_params)
    return verify_result.text == 'VERIFIED'


def create_preapproval(pledge):
    site = Site.objects.get_current()

    url = PP_API_URL + '/AdaptivePayments/Preapproval'

    data = {
        'returnUrl': 'http://%s%s' % (site,
            app_reverse('zipfelchappe_pledge_thankyou', 'zipfelchappe.urls')),
        'cancelUrl': 'http://%s%s' % (site,
            app_reverse('zipfelchappe_pledge_cancel', 'zipfelchappe.urls')),
        'ipnNotificationUrl': 'http://%s%s' % (site,
            reverse('zipfelchappe_paypal_ipn')),
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

    response = requests.post(url, headers=PP_REQ_HEADERS, data=json.dumps(data))

    return response


def create_payment(preapproval):
    site = Site.objects.get_current()

    pledge = preapproval.pledge

    url = PP_API_URL + '/AdaptivePayments/Pay'

    receivers = []

    if pledge.project.receivers.count() == 1:
        receiver = pledge.project.receivers.all()[0]
        amount = pledge.amount * (Decimal(receiver.percent)/Decimal('100.00'))

        receivers.append({
            'email': receiver.email,
            'amount': unicode(amount.quantize(Decimal('.01'))),
        })
    else:
        for receiver in pledge.project.receivers.all():
            amount = pledge.amount * (Decimal(receiver.percent)/Decimal('100.00'))

            receivers.append({
                'email': receiver.email,
                'amount': unicode(amount.quantize(Decimal('.01'))),
                'primary': receiver.primary,
            })

    data = {
        'actionType': 'PAY',
        'returnUrl': 'http://%s%s' % (site,
            app_reverse('zipfelchappe_pledge_thankyou', 'zipfelchappe.urls')),
        'cancelUrl': 'http://%s%s' % (site,
            app_reverse('zipfelchappe_pledge_cancel', 'zipfelchappe.urls')),
        'ipnNotificationUrl': 'http://%s%s' % (site,
            reverse('zipfelchappe_paypal_ipn')),
        'currencyCode': pledge.currency,
        'preapprovalKey': preapproval.key,
        'receiverList': {
            'receiver': receivers
        },
        'reverseAllParallelPaymentsOnError': True,
        'feesPayer': 'EACHRECEIVER',
        'memo': pledge.project.title,
        "requestEnvelope": {"errorLanguage":"en_US"},
    }

    r = requests.post(url, headers=PP_REQ_HEADERS, data=json.dumps(data))

    return r
