from rest_framework import serializers
from .models import Coupon, CouponUser


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'


class CouponUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponUser
        fields = '__all__'
