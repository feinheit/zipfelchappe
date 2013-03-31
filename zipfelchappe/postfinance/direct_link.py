from xml.etree import ElementTree

import requests


from .app_settings import POSTFINANCE



def request_payment(payment):
    env = 'prod' if POSTFINANCE['LIVE'] else 'test'
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
        payment.PM = ncresponse.attrib['NCERROR']
        payment.save()

        print ncresponse.attrib
    except ElementTree.ParseError:
        print res
