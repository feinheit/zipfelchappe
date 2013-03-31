import json
from datetime import timedelta
from django.utils import timezone

from django.core.management.base import BaseCommand

from zipfelchappe.models import Project, Pledge
from zipfelchappe.postfinance.models import Payment
from zipfelchappe.postfinance.direct_link import request_payment


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Executes the paypal payments for all successfully financed projects
        that end within the next 24 hours. Use with cronjob.
        For each payment an IPN model is created because payments are not immediate.
        Paypal sends a callback if the payments were successful.
        """

        # For all projects that end within the next 24 hours ...
        projects = Project.objects.filter(
            end__gte=timezone.now(),
            end__lte=timezone.now()+timedelta(days=1)
        )

        # ... get all authorized authorized payments ...
        pledges = Pledge.objects.filter(
            project__in=projects,
            status=Pledge.AUTHORIZED
        )

        # ... with a postfinance payment that has been authorized
        payments = Payment.objects.filter(
            pledge__in=pledges,
            STATUS='5'
        )

        for payment in payments:
            request_payment(payment)

        #print payments
