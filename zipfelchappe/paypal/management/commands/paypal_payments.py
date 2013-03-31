import json
from datetime import timedelta
from django.utils import timezone

from django.core.management.base import BaseCommand

from zipfelchappe.models import Project, Pledge
from zipfelchappe.paypal.paypal_api import process_payments


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

        pledges = Pledge.objects.filter(
            project__in=projects,
            status=Pledge.AUTHORIZED
        )

        pledges_paid = process_payments(pledges)
        print "Total pledges payed: %d" % pledges_paid
