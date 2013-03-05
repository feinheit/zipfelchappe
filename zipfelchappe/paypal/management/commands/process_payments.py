import json
from datetime import timedelta
from django.utils import timezone

from django.core.management.base import BaseCommand

from zipfelchappe.models import Project, Pledge

from zipfelchappe.paypal.models import Preapproval, Payment
from zipfelchappe.paypal.paypal_api import create_payment


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Executes the paypal payments for all successfully financed projects
        that end within the next 24 hours. Use with cronjob.
        For each payment an IPN model is created because payments are not immediate.
        Paypal sends a callback if the payments were successful.
        """

        # Get all projects that end within the next 24 hours.
        projects = Project.objects.filter(
            end__gte=timezone.now(),
            end__lte=timezone.now()+timedelta(days=1)
        )

        pledges_paid = 0

        for project in projects:
            if project.is_financed:
                for pledge in project.pledges.filter(status=Pledge.AUTHORIZED):
                    try:
                        preapproval = pledge.preapproval
                        # Check if pledge has a promising paypal preapproval key
                        if preapproval.status == 'ACTIVE' and preapproval.approved:
                            # Execute paypal payment
                            pp_payment = create_payment(preapproval)

                            if not pp_payment.ok or pp_payment.json() is None:
                                print pp_payment.text
                            elif 'error' in pp_payment.json():
                                print "ERROR CREATING PAYMENT: "
                                print json.dumps(pp_payment.json(), indent=2)
                            else:
                                # Payment was successful, change pledge state to paid
                                Payment.objects.create(
                                    key=pp_payment.json()['payKey'],
                                    preapproval=preapproval,
                                    status=pp_payment.json()['paymentExecStatus'],
                                    data=json.dumps(pp_payment.json(), indent=2),
                                )

                                pledge.status = Pledge.PAID
                                pledge.save()

                                print "PAYMENT FOR PLEDGE %s CREATED" % pledge
                                pledges_paid += 1
                        else:
                            print "PLEDGE NOT APPROVED: %s" % pledge

                    except Preapproval.DoesNotExist:
                        pass

        print "Total pledges payed: %d" % pledges_paid
