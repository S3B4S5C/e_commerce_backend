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
    fcm_token = models.CharField(max_length=255, null=True)
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


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        LOW_STOCK = 'LOW_STOCK', 'Stock mínimo'
        NEW_PRODUCT = 'NEW_PRODUCT', 'Nuevo producto'
        ORDER_ACCEPTED = 'ORDER_ACCEPTED', 'Pedido aceptado'
        OTHER = 'OTHER', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=30, choices=NotificationType.choices)
    title = models.TextField(null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.email} - {self.type}"


class UserNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    notification = models.ForeignKey('Notification', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'notification')

    def __str__(self):
        return f"{self.user.email} - {self.notification.type}"
