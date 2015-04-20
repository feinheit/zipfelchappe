from xml.etree import ElementTree

import requests
import logging
from zipfelchappe.postfinance.app_settings import POSTFINANCE

env = 'prod' if POSTFINANCE['LIVE'] else 'test'
api_logger = logging.getLogger('zipfelchappe.postfinance.api')


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
    api_logger.debug('Requesting payment for ID {0}\n{1}'.format(
        payid, response.text
    ))
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
    api_logger.debug('Updating payment for PayID {0}\n{1}'.format(
        payid, response.text
    ))
    ncresponse = ElementTree.fromstring(response.text)
    return ncresponse.attrib.copy()
