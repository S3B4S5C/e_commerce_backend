# App: logs/models.py
from django.db import models
import uuid


class ActivityLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=255, null=True)
    user = models.ForeignKey('users.UserAccount', on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    entity_id = models.UUIDField()
    time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
