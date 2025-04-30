from rest_framework import serializers
from .models import Order, OrderItem, PaymentDetail, ShippingMethod, OrderStatus


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity']


class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDetail
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    payment_detail = PaymentDetailSerializer()

    class Meta:
        model = Order
        fields = ['shipping_method', 'date', 'time', 'total_price', 'payment_detail', 'items']

    def create(self, validated_data):
        payment_data = validated_data.pop('payment_detail')
        items_data = validated_data.pop('items')
        user = self.context['request'].user

        # Crear detalles de pago
        payment = PaymentDetail.objects.create(**payment_data)

        # Crear orden
        order = Order.objects.create(
            user=user,
            payment_detail=payment,
            status_id=1,  # Por defecto, "Pendiente" u otro ID que definas
            **validated_data
        )

        for item in items_data:
            OrderItem.objects.create(
                order=order,
                product_id=item['product_id'],
                quantity=item['quantity']
            )

        return order


class StripePaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(default='usd')
    payment_method_id = serializers.CharField()


class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = '__all__'


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = '__all__'
