from rest_framework import serializers
from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    time = serializers.DateTimeField()

    class Meta:
        model = ActivityLog
        fields = ['id', 'type', 'description', 'user', 'time']

    def get_description(self, obj):
        return obj.description