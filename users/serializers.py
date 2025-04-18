from rest_framework import serializers
from .models import UserAccount, Role

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
        
class UserAccountSerializer(serializers.ModelSerializer):
    print("Iniciando el proceso de creación del usuario")
    class Meta:
        model = UserAccount
        fields  = '__all__'
        read_only_fields = ['id']
        