import json
from datetime import timedelta
from django.utils import timezone

from django.core.management.base import BaseCommand

from zipfelchappe.postfinance.models import Payment
from zipfelchappe.postfinance.direct_link import update_payment


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Check the status of postfinance payments that are in state "processing".
        """
        payments = Payment.objects.filter(STATUS='91')

        for payment in payments:
            update_payment(payment)
