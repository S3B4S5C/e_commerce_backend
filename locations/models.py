# App: locations/models.py
from django.db import models
import uuid
from users.models import UserAccount

class Coordinate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lon = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()

class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    coordinate = models.OneToOneField(Coordinate, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()

class AddressUser(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()

    class Meta:
        unique_together = ('user', 'address')

class Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    deleted_at = models.DateTimeField(null=True, blank=True)
