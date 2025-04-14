# App: payments/models.py
from django.db import models
import uuid

class PaymentMethod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50)
    number = models.CharField(max_length=19)
    expire_date = models.DateField()
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()

class Coupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expiration_date = models.DateField()
    type = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    discount = models.IntegerField()
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()

class CouponUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    user = models.ForeignKey('users.UserAccount', on_delete=models.CASCADE)
    use_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
