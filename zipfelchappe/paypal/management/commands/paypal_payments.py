from django.core.management.base import BaseCommand

from zipfelchappe.paypal.tasks import process_payments


class Command(BaseCommand):
    help = 'Collect all paypal payments for finished projects (cronjob)'

    def handle(self, *args, **options):
        pledges_processed = process_payments()
        print "Total pledges processed: %d" % pledges_processed
