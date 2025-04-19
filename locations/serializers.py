from rest_framework import serializers
from .models import Address, Coordinate


class CoordinateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinate
        fields = '__all__'
        read_only_fields = ['id']


class AddressSerializer(serializers.ModelSerializer):
    coordinate = CoordinateSerializer()

    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['id']

    def create(self, validated_data):
        coord_data = validated_data.pop('coordinate')
        coordinate = Coordinate.objects.create(**coord_data)
        address = Address.objects.create(coordinate=coordinate, **validated_data)
        return address


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['country', 'city', 'street', 'reference']
