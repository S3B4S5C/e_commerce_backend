# App: users/models.py
from django.db import models
import uuid

class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

class UserAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    email = models.EmailField()
    cellphone = models.CharField(max_length=20)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    deleted_at = models.DateTimeField(null=True, blank=True)