import json
from datetime import timedelta
from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError

from zipfelchappe.models import Project, Pledge

from zipfelchappe.paypal.models import Preapproval, Payment
from zipfelchappe.paypal.paypal_api import create_payment
from zipfelchappe import emails

class Command(BaseCommand):

    def handle(self, *args, **options):

        projects = Project.objects.filter(end__lte=timezone.now()+timedelta(days=1))

        pledges_payed = 0

        for project in projects:
            if project.is_financed:
                for pledge in project.pledges.filter(status=Pledge.AUTHORIZED):
                    try:
                        preapproval = pledge.preapproval
                        if preapproval.status == 'ACTIVE' and preapproval.approved:
                            pp_payment = create_payment(preapproval)

                            if not pp_payment.ok or pp_payment.json() is None:
                                print pp_payment.text
                            elif 'error' in pp_payment.json():
                                print "ERROR CREATING PAYMENT: "
                                print json.dumps(pp_payment.json(), indent=2)
                            else:
                                payment = Payment.objects.create(
                                    key = pp_payment.json()['payKey'],
                                    preapproval = preapproval,
                                    status = pp_payment.json()['paymentExecStatus'],
                                    data = json.dumps(pp_payment.json(), indent=2),
                                )

                                pledge.status = Pledge.PAID
                                pledge.save()

                                print "PAYMENT FOR PLEDGE %s CREATED" % pledge
                                pledges_payed += 1
                        else:
                            print "PLEDGE NOT APPROVED: %s" % pledge

                    except Preapproval.DoesNotExist:
                        pass

        print "Total pledges payed: %d" % pledges_payed
