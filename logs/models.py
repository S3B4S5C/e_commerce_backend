# App: logs/models.py
from django.db import models
import uuid

class ActivityLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.UserAccount', on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    table_affected = models.CharField(max_length=100)
    entity_id = models.UUIDField()
    timestamp = models.DateTimeField(auto_now_add=True)
