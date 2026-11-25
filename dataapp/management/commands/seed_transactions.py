import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from dataapp.models import Transaction


class Command(BaseCommand):
    help = 'Seed a large transactions table for Elldy Brick testing.'

    def add_arguments(self, parser):
        parser.add_argument('--rows', type=int, default=100000)
        parser.add_argument('--batch-size', type=int, default=5000)
        parser.add_argument('--clear', action='store_true')

    def handle(self, *args, **options):
        total_rows = options['rows']
        batch_size = options['batch_size']

        if options['clear']:
            self.stdout.write('Deleting existing transactions...')
            Transaction.objects.all().delete()

        categories = ['Electronics', 'Fashion', 'Grocery', 'Healthcare', 'Furniture', 'Automotive']
        payments = ['UPI', 'Credit Card', 'Debit Card', 'Cash', 'Net Banking']
        cities = ['Hyderabad', 'Bengaluru', 'Mumbai', 'Delhi', 'Chennai', 'Pune', 'Kolkata']
        statuses = ['Completed', 'Pending', 'Cancelled', 'Refunded']
        start_date = datetime(2024, 1, 1)

        created = 0
        while created < total_rows:
            current_batch = min(batch_size, total_rows - created)
            objects = []

            for _ in range(current_batch):
                quantity = random.randint(1, 10)
                price = Decimal(str(round(random.uniform(100, 25000), 2)))
                dt = start_date + timedelta(
                    days=random.randint(0, 900),
                    seconds=random.randint(0, 86399),
                )

                objects.append(
                    Transaction(
                        transaction_date=timezone.make_aware(dt),
                        customer_id=random.randint(1, 50000),
                        product_id=random.randint(1, 5000),
                        category=random.choice(categories),
                        quantity=quantity,
                        unit_price=price,
                        amount=price * quantity,
                        payment_method=random.choice(payments),
                        city=random.choice(cities),
                        status=random.choice(statuses),
                    )
                )

            Transaction.objects.bulk_create(objects, batch_size=batch_size)
            created += current_batch
            self.stdout.write(f'Inserted {created:,} / {total_rows:,}')

        self.stdout.write(self.style.SUCCESS(f'Done. Added {total_rows:,} transaction rows.'))
