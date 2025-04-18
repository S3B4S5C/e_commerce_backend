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
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        print("🔥 Método create ejecutado")  # Este print ya sabemos que aparece
        validated_data['email'] = validated_data['email'].lower()
        password = validated_data.pop('password')
        
        print(f"Contraseña antes de hashear: {password}")  # Verificamos la contraseña
        
        user = UserAccount(**validated_data)
        user.set_password(password)  # 🔒 Se espera que aquí se hashee
        
        print(f"Contraseña hasheada: {user.password}")  # Verificamos si se ha hasheado
        user.save(update_fields=['password'])
        return user
  