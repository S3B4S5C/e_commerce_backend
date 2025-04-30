from rest_framework import serializers
from .models import UserAccount, Role, Notification, UserNotification


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserAccountSerializer(serializers.ModelSerializer):
    print("Iniciando el proceso de creación del usuario")

    class Meta:
        model = UserAccount
        fields = '__all__'
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAccount
        fields = ['name', 'email', 'cellphone', 'birth_date', 'gender']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'message', 'created_at']


class UserNotificationSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer()

    class Meta:
        model = UserNotification
        fields = ['id', 'notification', 'is_read', 'received_at']
