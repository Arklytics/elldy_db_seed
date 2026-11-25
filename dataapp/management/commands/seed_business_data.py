import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from dataapp.models import (
    Customer,
    Supplier,
    Product,
    Employee,
    Order,
    OrderItem,
    Payment,
    Shipment,
    Return,
    InventoryMovement,
)


class Command(BaseCommand):
    help = "Seed realistic business data for analytics testing."

    def add_arguments(self, parser):
        parser.add_argument("--rows", type=int, default=10000)
        parser.add_argument("--clear", action="store_true")

    def handle(self, *args, **options):
        rows = options["rows"]

        if options["clear"]:
            InventoryMovement.objects.all().delete()
            Return.objects.all().delete()
            Shipment.objects.all().delete()
            Payment.objects.all().delete()
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Product.objects.all().delete()
            Supplier.objects.all().delete()
            Employee.objects.all().delete()
            Customer.objects.all().delete()

        cities = [
            "Hyderabad", "Bengaluru", "Mumbai",
            "Delhi", "Chennai", "Pune", "Kolkata"
        ]

        states = [
            "Telangana", "Karnataka", "Maharashtra",
            "Delhi", "Tamil Nadu", "West Bengal"
        ]

        categories = [
            "Electronics", "Fashion", "Grocery",
            "Healthcare", "Furniture", "Automotive"
        ]

        departments = [
            "Sales", "Operations", "Finance",
            "Support", "Marketing"
        ]

        start_date = datetime(2024, 1, 1)

        self.stdout.write("Seeding customers...")

        Customer.objects.bulk_create([
            Customer(
                name=f"Customer {i}",
                email=f"customer{i}@example.com",
                city=random.choice(cities),
                state=random.choice(states),
                segment=random.choice(
                    ["Retail", "SMB", "Enterprise"]
                ),
                joined_date=(
                    start_date + timedelta(
                        days=random.randint(0, 900)
                    )
                ).date(),
            )
            for i in range(1, rows + 1)
        ], batch_size=1000)

        self.stdout.write("Seeding suppliers...")

        Supplier.objects.bulk_create([
            Supplier(
                name=f"Supplier {i}",
                city=random.choice(cities),
                category=random.choice(categories),
                rating=Decimal(
                    str(round(random.uniform(2.5, 5.0), 2))
                ),
            )
            for i in range(1, rows + 1)
        ], batch_size=1000)

        supplier_ids = list(
            Supplier.objects.values_list("id", flat=True)
        )

        self.stdout.write("Seeding products...")

        Product.objects.bulk_create([
            Product(
                name=f"Product {i}",
                category=random.choice(categories),
                supplier_id=random.choice(supplier_ids),
                cost_price=Decimal(
                    str(round(random.uniform(100, 5000), 2))
                ),
                selling_price=Decimal(
                    str(round(random.uniform(500, 15000), 2))
                ),
                stock_quantity=random.randint(0, 2000),
            )
            for i in range(1, rows + 1)
        ], batch_size=1000)

        self.stdout.write("Seeding employees...")

        Employee.objects.bulk_create([
            Employee(
                name=f"Employee {i}",
                department=random.choice(departments),
                city=random.choice(cities),
                salary=Decimal(
                    str(round(random.uniform(25000, 120000), 2))
                ),
                joined_date=(
                    start_date + timedelta(
                        days=random.randint(0, 900)
                    )
                ).date(),
            )
            for i in range(1, rows + 1)
        ], batch_size=1000)

        customer_ids = list(
            Customer.objects.values_list("id", flat=True)
        )

        employee_ids = list(
            Employee.objects.values_list("id", flat=True)
        )

        product_ids = list(
            Product.objects.values_list("id", flat=True)
        )

        self.stdout.write("Seeding orders...")

        orders = []

        for _ in range(rows):
            total = Decimal(
                str(round(random.uniform(500, 50000), 2))
            )

            orders.append(
                Order(
                    customer_id=random.choice(customer_ids),
                    employee_id=random.choice(employee_ids),
                    order_date=timezone.make_aware(
                        start_date + timedelta(
                            days=random.randint(0, 900),
                            seconds=random.randint(0, 86399),
                        )
                    ),
                    status=random.choice([
                        "Completed",
                        "Pending",
                        "Cancelled",
                    ]),
                    total_amount=total,
                    city=random.choice(cities),
                )
            )

        Order.objects.bulk_create(
            orders,
            batch_size=1000
        )

        order_ids = list(
            Order.objects.values_list("id", flat=True)
        )

        self.stdout.write("Seeding order items...")

        OrderItem.objects.bulk_create([
            OrderItem(
                order_id=random.choice(order_ids),
                product_id=random.choice(product_ids),
                quantity=random.randint(1, 10),
                unit_price=Decimal(
                    str(round(random.uniform(500, 15000), 2))
                ),
                discount=Decimal(
                    str(round(random.uniform(0, 25), 2))
                ),
                line_total=Decimal(
                    str(round(random.uniform(500, 50000), 2))
                ),
            )
            for _ in range(rows)
        ], batch_size=1000)

        self.stdout.write("Seeding payments...")

        Payment.objects.bulk_create([
            Payment(
                order_id=random.choice(order_ids),
                payment_date=timezone.make_aware(
                    start_date + timedelta(
                        days=random.randint(0, 900)
                    )
                ),
                method=random.choice([
                    "UPI",
                    "Credit Card",
                    "Debit Card",
                    "Cash",
                    "Net Banking",
                ]),
                amount=Decimal(
                    str(round(random.uniform(500, 50000), 2))
                ),
                status=random.choice([
                    "Success",
                    "Pending",
                    "Failed",
                ]),
            )
            for _ in range(rows)
        ], batch_size=1000)

        self.stdout.write("Seeding shipments...")

        Shipment.objects.bulk_create([
            Shipment(
                order_id=random.choice(order_ids),
                shipped_date=timezone.now() - timedelta(
                    days=random.randint(1, 180)
                ),
                delivered_date=timezone.now() - timedelta(
                    days=random.randint(0, 170)
                ),
                carrier=random.choice([
                    "BlueDart",
                    "Delhivery",
                    "DTDC",
                    "FedEx",
                ]),
                status=random.choice([
                    "Delivered",
                    "In Transit",
                    "Delayed",
                ]),
            )
            for _ in range(rows)
        ], batch_size=1000)

        self.stdout.write("Seeding returns...")

        Return.objects.bulk_create([
            Return(
                order_id=random.choice(order_ids),
                product_id=random.choice(product_ids),
                return_date=timezone.now() - timedelta(
                    days=random.randint(0, 180)
                ),
                reason=random.choice([
                    "Damaged",
                    "Wrong Item",
                    "Not Required",
                    "Quality Issue",
                ]),
                refund_amount=Decimal(
                    str(round(random.uniform(100, 15000), 2))
                ),
            )
            for _ in range(rows)
        ], batch_size=1000)

        self.stdout.write("Seeding inventory movements...")

        InventoryMovement.objects.bulk_create([
            InventoryMovement(
                product_id=random.choice(product_ids),
                movement_date=timezone.now() - timedelta(
                    days=random.randint(0, 365)
                ),
                movement_type=random.choice([
                    "IN",
                    "OUT",
                    "ADJUSTMENT",
                ]),
                quantity=random.randint(1, 100),
                warehouse=random.choice([
                    "Hyderabad WH",
                    "Mumbai WH",
                    "Bengaluru WH",
                ]),
            )
            for _ in range(rows)
        ], batch_size=1000)

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished seeding approximately {rows:,} rows per table."
            )
        )