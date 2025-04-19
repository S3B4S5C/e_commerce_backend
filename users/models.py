# App: users/models.py
from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)


class UserAccount(AbstractBaseUser):

    class RoleChoices(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        CLIENT = 'CLIENT', 'Client'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    cellphone = models.CharField(max_length=20)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10)
    old_role = models.ForeignKey(Role, on_delete=models.CASCADE, default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    role = models.CharField(
        max_length=10,
        choices=RoleChoices.choices,
        default=RoleChoices.CLIENT
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'cellphone', 'birth_date', 'gender', 'role']

    def __str__(self):
        return self.email
