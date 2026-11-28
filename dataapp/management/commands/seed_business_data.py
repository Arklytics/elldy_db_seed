
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max
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
    help = "Append realistic business data for Elldy pipeline testing."

    def add_arguments(self, parser):
        parser.add_argument("--rows", type=int, default=10000)
        parser.add_argument("--batch-size", type=int, default=1000)
        parser.add_argument("--days", type=int, default=30)
        parser.add_argument("--clear", action="store_true")

    def next_id(self, model):
        return (model.objects.aggregate(
            max_id=Max("id")
        )["max_id"] or 0) + 1

    @transaction.atomic
    def handle(self, *args, **options):

        rows = options["rows"]
        batch_size = options["batch_size"]
        days = options["days"]

        if rows <= 0 or batch_size <= 0 or days <= 0:
            raise CommandError(
                "Rows, batch size and days must be positive."
            )

        models = [
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
        ]

        if options["clear"]:
            self.stdout.write(
                self.style.WARNING("Deleting existing business data...")
            )

            for model in reversed(models):
                model.objects.all().delete()

        before_counts = {
            model.__name__: model.objects.count()
            for model in models
        }

        now = timezone.now()
        today = timezone.localdate()
        money = Decimal("0.01")

        city_states = {
            "Hyderabad": "Telangana",
            "Bengaluru": "Karnataka",
            "Mumbai": "Maharashtra",
            "Delhi": "Delhi",
            "Chennai": "Tamil Nadu",
            "Pune": "Maharashtra",
            "Kolkata": "West Bengal",
        }

        cities = list(city_states.keys())

        categories = [
            "Electronics",
            "Fashion",
            "Grocery",
            "Healthcare",
            "Furniture",
            "Automotive",
        ]

        departments = [
            "Sales",
            "Operations",
            "Finance",
            "Support",
            "Marketing",
        ]

        payment_methods = [
            "UPI",
            "Credit Card",
            "Debit Card",
            "Cash",
            "Net Banking",
        ]

        warehouses = [
            "Hyderabad WH",
            "Mumbai WH",
            "Bengaluru WH",
        ]

        carriers = [
            "BlueDart",
            "Delhivery",
            "DTDC",
            "FedEx",
        ]

        # -----------------------------------
        # CUSTOMERS
        # -----------------------------------

        self.stdout.write("Seeding customers...")

        customer_start = self.next_id(Customer)
        customers = []

        for i in range(customer_start, customer_start + rows):

            city = random.choice(cities)

            customers.append(
                Customer(
                    name=f"Customer {i}",
                    email=f"customer{i}@example.com",
                    city=city,
                    state=city_states[city],
                    segment=random.choice([
                        "Retail",
                        "SMB",
                        "Enterprise",
                    ]),
                    joined_date=today - timedelta(
                        days=random.randint(days + 4, days + 730)
                    ),
                )
            )

        Customer.objects.bulk_create(
            customers,
            batch_size=batch_size,
        )

        # -----------------------------------
        # SUPPLIERS
        # -----------------------------------

        self.stdout.write("Seeding suppliers...")

        supplier_start = self.next_id(Supplier)

        Supplier.objects.bulk_create([
            Supplier(
                name=f"Supplier {i}",
                city=random.choice(cities),
                category=random.choice(categories),
                rating=Decimal(
                    str(round(random.uniform(2.5, 5.0), 2))
                ),
            )
            for i in range(supplier_start, supplier_start + rows)
        ], batch_size=batch_size)

        supplier_ids = list(
            Supplier.objects.values_list("id", flat=True)
        )

        # -----------------------------------
        # PRODUCTS
        # -----------------------------------

        self.stdout.write("Seeding products...")

        product_start = self.next_id(Product)
        products = []

        for i in range(product_start, product_start + rows):

            cost = Decimal(
                str(round(random.uniform(100, 5000), 2))
            )

            margin = Decimal(
                str(round(random.uniform(1.15, 2.5), 2))
            )

            selling_price = (cost * margin).quantize(money)

            products.append(
                Product(
                    name=f"Product {i}",
                    category=random.choice(categories),
                    supplier_id=random.choice(supplier_ids),
                    cost_price=cost,
                    selling_price=selling_price,
                    stock_quantity=random.randint(100, 2000),
                )
            )

        Product.objects.bulk_create(
            products,
            batch_size=batch_size,
        )

        # -----------------------------------
        # EMPLOYEES
        # -----------------------------------

        self.stdout.write("Seeding employees...")

        employee_start = self.next_id(Employee)

        Employee.objects.bulk_create([
            Employee(
                name=f"Employee {i}",
                department=random.choice(departments),
                city=random.choice(cities),
                salary=Decimal(
                    str(round(random.uniform(25000, 120000), 2))
                ),
                joined_date=today - timedelta(
                    days=random.randint(days + 4, days + 730)
                ),
            )
            for i in range(employee_start, employee_start + rows)
        ], batch_size=batch_size)

        # -----------------------------------
        # LOAD MASTER DATA
        # -----------------------------------

        customers = list(
            Customer.objects.filter(
                joined_date__lte=today - timedelta(days=days + 3)
            ).values("id", "city")
        )

        employee_ids = list(
            Employee.objects.filter(
                joined_date__lte=today - timedelta(days=days + 3)
            ).values_list("id", flat=True)
        )

        products = list(
            Product.objects.values("id", "selling_price")
        )

        # -----------------------------------
        # BUSINESS TRANSACTIONS
        # -----------------------------------

        self.stdout.write("Seeding business transactions...")

        order_items = []
        payments = []
        shipments = []
        returns = []
        movements = []

        def flush_batches():

            OrderItem.objects.bulk_create(
                order_items,
                batch_size=batch_size,
            )

            Payment.objects.bulk_create(
                payments,
                batch_size=batch_size,
            )

            Shipment.objects.bulk_create(
                shipments,
                batch_size=batch_size,
            )

            Return.objects.bulk_create(
                returns,
                batch_size=batch_size,
            )

            InventoryMovement.objects.bulk_create(
                movements,
                batch_size=batch_size,
            )

            order_items.clear()
            payments.clear()
            shipments.clear()
            returns.clear()
            movements.clear()

        for index in range(rows):

            customer = random.choice(customers)

            # Leave enough time for delivery and returns.
            order_date = now - timedelta(
                days=random.randint(2, days + 1),
                seconds=random.randint(0, 86399),
            )

            status = random.choices(
                ["Completed", "Pending", "Cancelled"],
                weights=[85, 10, 5],
                k=1,
            )[0]

            warehouse = random.choice(warehouses)

            selected_products = random.sample(
                products,
                min(len(products), random.randint(1, 5)),
            )

            item_data = []
            total_amount = Decimal("0.00")

            for product in selected_products:

                quantity = random.randint(1, 10)
                price = product["selling_price"]
                discount = Decimal(random.randint(0, 20))

                line_total = (
                    price * quantity *
                    (Decimal("1") - discount / Decimal("100"))
                ).quantize(money)

                total_amount += line_total

                item_data.append({
                    "product_id": product["id"],
                    "quantity": quantity,
                    "unit_price": price,
                    "discount": discount,
                    "line_total": line_total,
                })

            # Individual creation ensures the order ID
            # is available on MySQL.

            order = Order.objects.create(
                customer_id=customer["id"],
                employee_id=random.choice(employee_ids),
                order_date=order_date,
                status=status,
                total_amount=total_amount,
                city=customer["city"],
            )

            # -----------------------------------
            # ORDER ITEMS AND INVENTORY
            # -----------------------------------

            for item in item_data:

                order_items.append(
                    OrderItem(
                        order_id=order.id,
                        product_id=item["product_id"],
                        quantity=item["quantity"],
                        unit_price=item["unit_price"],
                        discount=item["discount"],
                        line_total=item["line_total"],
                    )
                )

                if status == "Completed":

                    movements.append(
                        InventoryMovement(
                            product_id=item["product_id"],
                            movement_date=order_date,
                            movement_type="OUT",
                            quantity=item["quantity"],
                            warehouse=warehouse,
                        )
                    )

            # -----------------------------------
            # PAYMENTS
            # -----------------------------------

            payment_status = {
                "Completed": "Success",
                "Pending": "Pending",
                "Cancelled": "Failed",
            }[status]

            payments.append(
                Payment(
                    order_id=order.id,
                    payment_date=order_date + timedelta(minutes=10),
                    method=random.choice(payment_methods),
                    amount=total_amount,
                    status=payment_status,
                )
            )

            # -----------------------------------
            # SHIPMENTS
            # -----------------------------------

            if status == "Completed":

                shipped_date = order_date + timedelta(hours=2)

                delivered_date = shipped_date + timedelta(
                    hours=random.randint(6, 24)
                )

                shipments.append(
                    Shipment(
                        order_id=order.id,
                        shipped_date=shipped_date,
                        delivered_date=delivered_date,
                        carrier=random.choice(carriers),
                        status="Delivered",
                    )
                )

                # -----------------------------------
                # RETURNS
                # -----------------------------------

                if random.random() < 0.08:

                    returned_item = random.choice(item_data)

                    return_date = delivered_date + timedelta(
                        hours=random.randint(1, 6)
                    )

                    reason = random.choice([
                        "Damaged",
                        "Wrong Item",
                        "Not Required",
                        "Quality Issue",
                    ])

                    returns.append(
                        Return(
                            order_id=order.id,
                            product_id=returned_item["product_id"],
                            return_date=return_date,
                            reason=reason,
                            refund_amount=returned_item["line_total"],
                        )
                    )

                    # Restock only suitable returned items.
                    if reason in ["Wrong Item", "Not Required"]:

                        movements.append(
                            InventoryMovement(
                                product_id=returned_item["product_id"],
                                movement_date=return_date,
                                movement_type="IN",
                                quantity=returned_item["quantity"],
                                warehouse=warehouse,
                            )
                        )

            if (index + 1) % batch_size == 0:

                flush_batches()

                self.stdout.write(
                    f"Processed {index + 1:,} / {rows:,} orders"
                )

        # Insert remaining records.
        flush_batches()

        # -----------------------------------
        # FINAL SUMMARY
        # -----------------------------------

        self.stdout.write("\nBUSINESS DATA SEED SUMMARY")
        self.stdout.write("-" * 55)

        total_added = 0

        for model in models:

            name = model.__name__
            before = before_counts[name]
            after = model.objects.count()
            added = after - before

            total_added += added

            self.stdout.write(
                f"{name}: Before={before:,} | "
                f"Added={added:,} | Total={after:,}"
            )

        self.stdout.write("-" * 55)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully added {total_added:,} business records."
            )
        )
