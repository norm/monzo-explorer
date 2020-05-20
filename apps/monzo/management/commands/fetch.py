from django.core.management.base import BaseCommand

from apps.monzo.models import Transaction


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help=(
                'Fetch all transactions (needs a fresh auth, '
                + 'Monzo limit this to a 5 minute window).'
            )
        )

    def handle(self, *args, **options):
        Transaction.fetch_data_from_monzo(options['all'])
