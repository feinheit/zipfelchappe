from django.core.management.base import BaseCommand

from zipfelchappe.postfinance.tasks import update_payments


class Command(BaseCommand):

    help = 'Check status of all pending postfinance payments (cronjob)'

    def handle(self, *args, **options):
        payments_updated = update_payments()
        print "Total payments updated: %d " % payments_updated
