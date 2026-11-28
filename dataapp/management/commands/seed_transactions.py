
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from dataapp.models import Transaction


class Command(BaseCommand):
    help = "Append large transaction datasets for Elldy Brick testing."

    def add_arguments(self, parser):
        parser.add_argument("--rows", type=int, default=100000)
        parser.add_argument("--batch-size", type=int, default=5000)
        parser.add_argument("--days", type=int, default=30)
        parser.add_argument("--clear", action="store_true")

    def handle(self, *args, **options):

        total_rows = options["rows"]
        batch_size = options["batch_size"]
        days = options["days"]

        if total_rows <= 0 or batch_size <= 0 or days <= 0:
            raise CommandError(
                "Rows, batch size and days must be positive."
            )

        if options["clear"]:

            self.stdout.write(
                self.style.WARNING(
                    "Deleting existing transactions..."
                )
            )

            Transaction.objects.all().delete()

        before_count = Transaction.objects.count()

        self.stdout.write(
            f"Existing transactions: {before_count:,}"
        )

        categories = [
            "Electronics",
            "Fashion",
            "Grocery",
            "Healthcare",
            "Furniture",
            "Automotive",
        ]

        payments = [
            "UPI",
            "Credit Card",
            "Debit Card",
            "Cash",
            "Net Banking",
        ]

        cities = [
            "Hyderabad",
            "Bengaluru",
            "Mumbai",
            "Delhi",
            "Chennai",
            "Pune",
            "Kolkata",
        ]

        statuses = [
            "Completed",
            "Pending",
            "Cancelled",
            "Refunded",
        ]

        now = timezone.now()
        created = 0

        start_time = timezone.now()

        self.stdout.write(
            f"Generating {total_rows:,} new transactions..."
        )

        self.stdout.write(
            f"Batch size: {batch_size:,}"
        )

        self.stdout.write(
            f"Transaction date range: Last {days} days"
        )

        self.stdout.write("-" * 50)

        while created < total_rows:

            current_batch = min(
                batch_size,
                total_rows - created,
            )

            objects = []

            for _ in range(current_batch):

                quantity = random.randint(1, 10)

                price = Decimal(
                    str(round(random.uniform(100, 25000), 2))
                )

                amount = (
                    price * quantity
                ).quantize(Decimal("0.01"))

                transaction_date = now - timedelta(
                    seconds=random.randint(
                        0,
                        days * 86400,
                    )
                )

                category = random.choice(categories)

                status = random.choices(
                    statuses,
                    weights=[85, 7, 5, 3],
                    k=1,
                )[0]

                objects.append(
                    Transaction(
                        transaction_date=transaction_date,

                        customer_id=random.randint(
                            1, 50000
                        ),

                        product_id=random.randint(
                            1, 5000
                        ),

                        category=category,
                        quantity=quantity,
                        unit_price=price,
                        amount=amount,

                        payment_method=random.choice(
                            payments
                        ),

                        city=random.choice(cities),
                        status=status,
                    )
                )

            Transaction.objects.bulk_create(
                objects,
                batch_size=batch_size,
            )

            created += current_batch

            progress = (created / total_rows) * 100

            elapsed = (
                timezone.now() - start_time
            ).total_seconds()

            self.stdout.write(
                f"Inserted {created:,} / {total_rows:,} "
                f"({progress:.1f}%) | "
                f"Elapsed: {elapsed:.2f}s"
            )

        after_count = Transaction.objects.count()

        duration = (
            timezone.now() - start_time
        ).total_seconds()

        self.stdout.write("\nTRANSACTION SEED SUMMARY")
        self.stdout.write("-" * 50)

        self.stdout.write(
            f"Previous records : {before_count:,}"
        )

        self.stdout.write(
            f"Inserted records : {created:,}"
        )

        self.stdout.write(
            f"Total records    : {after_count:,}"
        )

        self.stdout.write(
            f"Execution time   : {duration:.2f} seconds"
        )

        self.stdout.write("-" * 50)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully added {created:,} transactions."
            )
        )
