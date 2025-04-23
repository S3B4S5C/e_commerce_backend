from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderSerializer, PaymentDetailSerializer, ShippingMethodSerializer, OrderStatusSerializer
import stripe
from products.models import Product, Stock
from django.utils import timezone
from .models import Order, PaymentDetail, OrderItem, OrderStatus, Invoice, ShippingMethod
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from cart.models import Cart, CartItem
from users.models import UserAccount, Notification


stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    serializer = OrderSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        order = serializer.save()
        return Response({'message': 'Pedido realizado con éxito', 'order_id': order.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_with_payment(request):
    user = request.user
    shipping_method_id = request.data.get('shipping_method_id')

    try:
        cart = Cart.objects.get(user=user, deleted_at__isnull=True)
    except Cart.DoesNotExist:
        return Response({'error': 'No hay un carrito activo para este usuario.'}, status=404)

    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items.exists():
        return Response({'error': 'El carrito está vacío.'}, status=400)

    # Validar stock suficiente
    for item in cart_items:
        try:
            stock = Stock.objects.get(product=item.product)
        except Stock.DoesNotExist:
            return Response({
                'error': f'El producto "{item.product.name}" no tiene registro de stock.'
            }, status=400)

        if item.quantity_product > stock.quantity:
            return Response({
                'error': f'El producto "{item.product.name}" no tiene suficiente stock. Disponible: {stock.quantity}.'
            }, status=400)

    total_price = sum(item.product.price * item.quantity_product for item in cart_items)

    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(float(total_price) * 100),
            currency='usd',
            metadata={'integration_check': 'accept_a_payment', 'user_id': str(user.id)}
        )
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=400)

    payment_detail = PaymentDetail.objects.create(
        stripe_payment_id=payment_intent.id,
        state='pendiente',
        provider='stripe',
        created_at=timezone.now(),
        modified_at=timezone.now()
    )

    status_obj = OrderStatus.objects.get(name='Pendiente')
    order = Order.objects.create(
        user=user,
        payment_detail=payment_detail,
        shipping_method_id=shipping_method_id,
        status=status_obj,
        date=timezone.now().date(),
        time=timezone.now().time(),
        total_price=total_price,
        created_at=timezone.now(),
        modified_at=timezone.now()
    )

    # Crear ítems del pedido y descontar stock
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity_product,
            created_at=timezone.now(),
            modified_at=timezone.now()
        )

        stock = Stock.objects.get(product=item.product)
        stock.quantity -= item.quantity_product
        stock.save()

        if stock.quantity < 5:
            admins = UserAccount.objects.filter(role=UserAccount.RoleChoices.ADMIN, is_active=True)

            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    type=Notification.NotificationType.LOW_STOCK,
                    message=f'El stock del producto "{item.product.name}" ha bajado a {stock.quantity} unidades.',
                )
    cart.deleted_at = timezone.now()
    cart.save()

    return Response({
        'message': 'Pedido creado correctamente desde el carrito',
        'order_id': order.id,
        'client_secret': payment_intent.client_secret
    }, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_payment_method(request):
    data = request.data.copy()
    data['created_at'] = datetime.now()
    data['modified_at'] = datetime.now()

    serializer = PaymentDetailSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Método de pago agregado', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_payment_method(request, payment_id):
    try:
        payment = PaymentDetail.objects.get(id=payment_id)
        payment.delete()
        return Response({'message': 'Método de pago eliminado'}, status=status.HTTP_200_OK)
    except PaymentDetail.DoesNotExist:
        return Response({'error': 'Método de pago no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_ordenes(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def confirmar_pago(request, payment_id):
    try:
        print("ID recibido:", payment_id)
        payment = PaymentDetail.objects.get(stripe_payment_id=payment_id)
        intent = stripe.PaymentIntent.retrieve(payment_id)
        print(intent.status)
        if intent.status == 'succeeded':
            payment.state = 'pagado'
            payment.save()

            # Crear factura
            Invoice.objects.create(
                order=payment.order,
                nit=request.data.get('nit', '0'),
                razon_social=request.data.get('razon_social', 'Consumidor final'),
                total_amount=payment.order.total_price
            )
            return Response({'message': 'Factura generada correctamente'})
        else:
            return Response({'error': 'El pago aún no se ha completado'}, status=400)

    except PaymentDetail.DoesNotExist:
        return Response({'error': 'Pago no encontrado'}, status=404)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = 'whsec_...'  # tu clave secreta de webhook

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        payment_id = intent['id']

        try:
            payment = PaymentDetail.objects.get(stripe_payment_id=payment_id)
            payment.state = 'pagado'
            payment.save()

            # Crear factura
            Invoice.objects.create(
                order=payment.order,
                nit='0',  # Aquí puedes tomar de request o del usuario
                razon_social='Consumidor final',
                total_amount=payment.order.total_price
            )

        except PaymentDetail.DoesNotExist:
            return JsonResponse({'error': 'PaymentDetail not found'}, status=404)

    return JsonResponse({'status': 'success'})


@api_view(['POST'])
def create_shipping_method(request):
    serializer = ShippingMethodSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Método de envío creado', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_shipping_method(request, method_id):
    try:
        method = ShippingMethod.objects.get(id=method_id)
        method.delete()
        return Response({'message': 'Método de envío eliminado'}, status=status.HTTP_200_OK)
    except ShippingMethod.DoesNotExist:
        return Response({'error': 'Método de envío no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_shipping_methods(request):
    methods = ShippingMethod.objects.all()
    serializer = ShippingMethodSerializer(methods, many=True)
    return Response({'shipping_methods': serializer.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_status(request):
    serializer = OrderStatusSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Estado creado con éxito', 'estado': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_order_status(request, name):
    try:
        status_obj = OrderStatus.objects.get(name=name)
        status_obj.delete()
        return Response({'message': f"Estado '{name}' eliminado correctamente."}, status=status.HTTP_204_NO_CONTENT)
    except OrderStatus.DoesNotExist:
        return Response({'error': f"Estado '{name}' no existe."}, status=status.HTTP_404_NOT_FOUND)
