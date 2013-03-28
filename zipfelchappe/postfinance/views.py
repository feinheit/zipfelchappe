"""
Payment module for Postfinance integration

Needs the following settings to work correctly::

    POSTFINANCE = {
        'PSPID': 'your_shop_id',
        'LIVE': True, # Or False
        'SHA1_IN': 'yourhash',
        'SHA1_OUT': 'yourotherhash',
        }
"""

from datetime import datetime
from decimal import Decimal
from hashlib import sha1
import locale
import logging

from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _, get_language, to_locale
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from feincms.content.application.models import app_reverse

from zipfelchappe.views import requires_pledge
from zipfelchappe.models import Pledge

from .app_settings import POSTFINANCE

logger = logging.getLogger('zipfelchappe.postfinance.ipn')

STATUS_DICT = {
    '0' : 'Incomplete or invalid',
    '1' : 'Cancelled by client',
    '2' : 'Authorization refused',
    '4' : 'Order stored',
    '41': 'Waiting client payment',
    '5' : 'Authorized',
    '51': 'Authorization waiting',
    '52': 'Authorization not known',
    '55': 'Stand-by',
    '59': 'Authoriz. to get manually',
    '6' : 'Authorized and cancelled',
    '61': 'Author. deletion waiting',
    '62': 'Author. deletion uncertain',
    '63': 'Author. deletion refused',
    '64': 'Authorized and cancelled',
    '7' : 'Payment deleted',
    '71': 'Payment deletion pending',
    '72': 'Payment deletion uncertain',
    '73': 'Payment deletion refused',
    '74': 'Payment deleted',
    '75': 'Deletion processed by merchant',
    '8' : 'Refund',
    '81': 'Refund pending',
    '82': 'Refund uncertain',
    '83': 'Refund refused',
    '84': 'Payment declined by the acquirer',
    '85': 'Refund processed by merchant',
    '9' : 'Payment requested',
    '91': 'Payment processing',
    '92': 'Payment uncertain',
    '93': 'Payment refused',
    '94': 'Refund declined by the acquirer',
    '95': 'Payment processed by merchant',
    '99': 'Being processed',
}


@requires_pledge
def payment(request, pledge):
    site = Site.objects.get_current()

    logger.info('Processing using Postfinance')

    # Create db something here

    form_params = {
        'orderID': 'pledge-%d' % (pledge.id),
        'amount': u'%s' % int(pledge.amount.quantize(Decimal('0.00'))*100),
        'currency': pledge.currency,
        'PSPID': POSTFINANCE['PSPID'],
        'mode': POSTFINANCE['LIVE'] and 'prod' or 'test',
    }

    form_params['SHASign'] = sha1(u''.join((
        form_params['orderID'],
        form_params['amount'],
        form_params['currency'],
        form_params['PSPID'],
        POSTFINANCE['SHA1_IN'],
    ))).hexdigest()

    accept_url = 'http://%s%s' % (request.get_host(),
            app_reverse('zipfelchappe_pledge_thankyou', 'zipfelchappe.urls'))

    cancel_url = 'http://%s%s' % (request.get_host(),
            app_reverse('zipfelchappe_pledge_cancel', 'zipfelchappe.urls'))

    return render(request, 'zipfelchappe/postfinance_form.html', {
        'pledge': pledge,
        'form_params': form_params,
        'locale': locale.normalize(to_locale(get_language())).split('.')[0],
        'accept_url': accept_url,
        'decline_url': '',
        'exception_url': '',
        'cancel_url': cancel_url,
    })

@csrf_exempt
def ipn(request):
    POSTFINANCE = settings.POSTFINANCE

    try:
        parameters_repr = repr(request.POST.copy()).encode('utf-8')
        logger.info('IPN: Processing request data %s' % parameters_repr)

        try:
            orderID = request.POST['orderID']
            currency = request.POST['currency']
            amount = request.POST['amount']
            PM = request.POST['PM']
            ACCEPTANCE = request.POST['ACCEPTANCE']
            STATUS = request.POST['STATUS']
            CARDNO = request.POST['CARDNO']
            PAYID = request.POST['PAYID']
            NCERROR = request.POST['NCERROR']
            BRAND = request.POST['BRAND']
            SHASIGN = request.POST['SHASIGN']
        except KeyError:
            logger.error('IPN: Missing data in %s' % parameters_repr)
            return HttpResponseForbidden('Missing data')

        sha1_source = u''.join((
            orderID,
            currency,
            amount,
            PM,
            ACCEPTANCE,
            STATUS,
            CARDNO,
            PAYID,
            NCERROR,
            BRAND,
            POSTFINANCE['SHA1_OUT'],
        ))

        sha1_out = sha1(sha1_source).hexdigest()

        if sha1_out.lower() != SHASIGN.lower():
            logger.error('IPN: Invalid hash in %s' % parameters_repr)
            return HttpResponseForbidden('Hash did not validate')

        try:
            pledge_id = orderID.split('-')[1]
        except (ValueError, IndexError):
            logger.error('IPN: Error getting order for %s' % orderID)
            return HttpResponseForbidden('Malformed order ID')

        try:
            pledge = Pledge.objects.get(pk=pledge_id)
        except Pledge.DoesNotExist:
            logger.error('IPN: Pledge %s does not exist' % pledge_id)
            return HttpResponseForbidden('Pledge %s does not exist' % pledge_id)

        # TODO: Capture ipn data into DB transaction here
        # transaction.currency = currency
        # transaction.amount = Decimal(amount)
        # transaction.data = request.POST.copy()
        # transaction.transaction_id = PAYID
        # transaction.payment_method = BRAND
        # transaction.notes = STATUS_DICT.get(STATUS)

        logger.info('IPN: Status = %s' % STATUS)
        if STATUS == '5':
            pledge.status = Pledge.AUTHORIZED
        if STATUS == '9':
            pledge.status = Pledge.PAID

        pledge.save()
        logger.info('IPN: Successfully processed IPN request for %s' % order)
        return HttpResponse('OK')
    except Exception, e:
        logger.error('IPN: Processing failure %s' % unicode(e))
        raise
