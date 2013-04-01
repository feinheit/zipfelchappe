from xml.etree import ElementTree

import requests

from zipfelchappe.models import Pledge

from .app_settings import POSTFINANCE

env = 'prod' if POSTFINANCE['LIVE'] else 'test'

def update_payment(payment):
    url = 'https://e-payment.postfinance.ch/ncol/%s/querydirect.asp' % env
    payload = {
        'PSPID': POSTFINANCE['PSPID'],
        'USERID': POSTFINANCE['USERID'],
        'PSWD': POSTFINANCE['PSWD'],
        'PAYID': payment.PAYID,
    }

    res = requests.post(url, data=payload)
    try:
        ncresponse = ElementTree.fromstring(res.text)

        payment.STATUS = ncresponse.attrib['STATUS']
        payment.save()

        if payment.STATUS == '9':
            payment.pledge.status = Pledge.PAID
            payment.pledge.save()

    except ElementTree.ParseError:
        print "Parsing Error:\n", res


def request_payment(payment):
    url = 'https://e-payment.postfinance.ch/ncol/%s/maintenancedirect.asp' % env
    payload = {
        'PSPID': POSTFINANCE['PSPID'],
        'USERID': POSTFINANCE['USERID'],
        'PSWD': POSTFINANCE['PSWD'],
        'PAYID': payment.PAYID,
        'OPERATION': 'SAS' # Request payment and close transaction
    }

    res = requests.post(url, data=payload)

    try:
        ncresponse = ElementTree.fromstring(res.text)

        payment.STATUS = ncresponse.attrib['STATUS']
        payment.save()
    except ElementTree.ParseError:
        print "Parsing Error:\n", res
  
