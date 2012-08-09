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

        projects = Project.objects.filter(end__lte=timezone.now())

        for project in projects:
            if project.is_financed:
                if not hasattr(project, 'receivers') or not project.receivers.count():
                    print('Project %s has no paypal receivers!\n'
                           'Please activate the extension and define at least one '
                           'receiver in the admin.' % project)
                    continue

                for pledge in project.pledges.filter(status=Pledge.AUTHORIZED):
                    try:
                        preapproval = pledge.preapproval
                        if preapproval.status == 'ACTIVE' and preapproval.approved:
                            pp_payment = create_payment(preapproval)

                            payment_json = json.dumps(pp_payment.json, indent=2)

                            if 'error' in pp_payment.json:
                                print "ERROR CREATING PAYMENT: "
                                print payment_json
                            else:
                                payment = Payment.objects.create(
                                    key = pp_payment.json['payKey'],
                                    preapproval = preapproval,
                                    status = pp_payment.json['paymentExecStatus'],
                                    data = payment_json,
                                )

                                print "PAYMENT FOR PLEDGE %s CREATED" % pledge

                                emails.send_successfull_message(project, pledge)
                        else:
                            print "PLEDGE NOT APPROVED: %s" % pledge

                    except Preapproval.DoesNotExist:
                        pass
