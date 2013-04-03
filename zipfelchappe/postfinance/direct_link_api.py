from xml.etree import ElementTree

import requests

from .app_settings import POSTFINANCE

env = 'prod' if POSTFINANCE['LIVE'] else 'test'


def request_payment(payid):
    """ request payment of payid and close transaction """
    url = 'https://e-payment.postfinance.ch/ncol/%s/maintenancedirect.asp' % env
    payload = {
        'PSPID': POSTFINANCE['PSPID'],
        'USERID': POSTFINANCE['USERID'],
        'PSWD': POSTFINANCE['PSWD'],
        'PAYID': payid,
        'OPERATION': 'SAS'
    }

    response = requests.post(url, data=payload)

    ncresponse = ElementTree.fromstring(response.text)
    return ncresponse.attrib.copy()


def update_payment(payid):
    url = 'https://e-payment.postfinance.ch/ncol/%s/querydirect.asp' % env
    payload = {
        'PSPID': POSTFINANCE['PSPID'],
        'USERID': POSTFINANCE['USERID'],
        'PSWD': POSTFINANCE['PSWD'],
        'PAYID': payid,
    }

    response = requests.post(url, data=payload)

    ncresponse = ElementTree.fromstring(response.text)
    return ncresponse.attrib.copy()
