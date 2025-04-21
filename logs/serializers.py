from rest_framework import serializers
from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    time = serializers.DateTimeField(source='timestamp')

    class Meta:
        model = ActivityLog
        fields = ['id', 'table_affected', 'description', 'user', 'time']

    def get_description(self, obj):
        return obj.action
