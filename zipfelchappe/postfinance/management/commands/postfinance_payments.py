from django.core.management.base import BaseCommand

from zipfelchappe.postfinance.tasks import process_payments


class Command(BaseCommand):

    help = 'Collect all postfinance payments for finished projects (cronjob)'

    def handle(self, *args, **options):
        payments_processed = process_payments()
        print "Total payments processed: %d " % payments_processed
