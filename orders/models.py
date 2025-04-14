# App: orders/models.py
from django.db import models
import uuid
from datetime import timedelta

class PaymentDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.CharField(max_length=50)
    provider = models.CharField(max_length=50)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()

class ShippingMethod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_time = models.DurationField(default=timedelta(0))

class OrderStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.UserAccount', on_delete=models.CASCADE)
    payment_detail = models.ForeignKey(PaymentDetail, on_delete=models.CASCADE)
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE)
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    deleted_at = models.DateTimeField(null=True, blank=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()

    class Meta:
        unique_together = ('order', 'product')

class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    nit = models.CharField(max_length=50, default='0')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    razon_social = models.CharField(max_length=50, default='Ninguna')
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()