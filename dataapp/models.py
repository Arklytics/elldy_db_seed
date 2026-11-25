from django.db import models


# Existing transaction table
class Transaction(models.Model):
    transaction_date = models.DateTimeField(db_index=True)
    customer_id = models.BigIntegerField(db_index=True)
    product_id = models.IntegerField(db_index=True)
    category = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    status = models.CharField(max_length=30)

    class Meta:
        db_table = "transactions"
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["city"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Transaction {self.id}"


class Customer(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100)
    segment = models.CharField(max_length=50, db_index=True)
    joined_date = models.DateField(db_index=True)

    class Meta:
        db_table = "customers"


class Supplier(models.Model):
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    category = models.CharField(max_length=100, db_index=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        db_table = "suppliers"


class Product(models.Model):
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=100, db_index=True)

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="products",
    )

    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    stock_quantity = models.IntegerField()

    class Meta:
        db_table = "products"


class Employee(models.Model):
    name = models.CharField(max_length=150)
    department = models.CharField(
        max_length=100,
        db_index=True
    )
    city = models.CharField(max_length=100)

    salary = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    joined_date = models.DateField()

    class Meta:
        db_table = "employees"


class Order(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    order_date = models.DateTimeField(db_index=True)

    status = models.CharField(
        max_length=30,
        db_index=True
    )

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    city = models.CharField(
        max_length=100,
        db_index=True
    )

    class Meta:
        db_table = "orders"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="order_items",
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    discount = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    line_total = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    class Meta:
        db_table = "order_items"


class Payment(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    payment_date = models.DateTimeField(db_index=True)

    method = models.CharField(
        max_length=50,
        db_index=True
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    status = models.CharField(
        max_length=30,
        db_index=True
    )

    class Meta:
        db_table = "payments"


class Shipment(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="shipments",
    )

    shipped_date = models.DateTimeField(
        null=True,
        blank=True
    )

    delivered_date = models.DateTimeField(
        null=True,
        blank=True
    )

    carrier = models.CharField(
        max_length=100,
        db_index=True
    )

    status = models.CharField(
        max_length=30,
        db_index=True
    )

    class Meta:
        db_table = "shipments"


class Return(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="returns",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="returns",
    )

    return_date = models.DateTimeField(db_index=True)

    reason = models.CharField(
        max_length=150,
        db_index=True
    )

    refund_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    class Meta:
        db_table = "returns"


class InventoryMovement(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory_movements",
    )

    movement_date = models.DateTimeField(db_index=True)

    movement_type = models.CharField(
        max_length=30,
        db_index=True
    )

    quantity = models.IntegerField()

    warehouse = models.CharField(
        max_length=100,
        db_index=True
    )

    class Meta:
        db_table = "inventory_movements"