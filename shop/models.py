from django.db import models
from django.utils import timezone


class Address(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.IntegerField()
    country = models.CharField(max_length=50)

    def __str__(self):
        return str(self.street) + ":" + str(self.zip_code)


class User(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    shipping_address = models.ForeignKey(Address, max_length=60, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name) + ':' + str(self.phone)


class Buyer(models.Model):
    buyer_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.buyer_id)


class Seller(models.Model):
    seller_id = models.ForeignKey(User, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    def __str__(self):
        return str(self.user_name)


class Category(models.Model):
    name = models.TextField()

    def __str__(self):
        return str(self.name)


class Product(models.Model):
    product_name = models.CharField(max_length=50)
    product_description = models.TextField(blank=True)
    product_price = models.FloatField(default=0.0)
    product_available_count = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_seller = models.ForeignKey(Seller, max_length=60, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.product_name)


class Cart(models.Model):
    customer = models.ForeignKey(Buyer, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.customer)


class Ledger(models.Model):
    transaction_date = models.DateTimeField(default=timezone.now)
    amount = models.FloatField(default=0.0)
    customer = models.ForeignKey(Buyer, on_delete=models.CASCADE)


class Order(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product_id = models.ManyToManyField(Product)
    amount = models.FloatField(default=0.0)

    def __str__(self):
        return str(self.cart) + ':' + str(self.product_id)


class Shipment(models.Model):
    UNSHIPPED = 0
    SHIPPED = 1
    COMPLETED = 2
    CANCELED = 3
    REFUND_APPLIED = 4

    Shipment_status = (
        (UNSHIPPED, "not shiped"),
        (SHIPPED, "shiped"),
        (COMPLETED, "delivered"),
        (CANCELED, "cancelled"),
        (REFUND_APPLIED, "refund applied")
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=Shipment_status)
    shipment_date = models.DateTimeField(default=timezone.now)
