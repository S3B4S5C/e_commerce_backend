from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import CouponSerializer, CouponUserSerializer, PaymentMethodSerializer
from rest_framework.permissions import IsAuthenticated
from .models import CouponUser, Coupon, PaymentMethod
from users.views import add_notifications
from users.permisions import IsAdminRole


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_payment_method(request):
    """
    Agrega un método de pago al usuario autenticado.
    """
    serializer = PaymentMethodSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({'message': 'Método de pago agregado exitosamente.', 'payment_method': serializer.data},
                        status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_payment_method(request, method_id):
    """
    Elimina un método de pago específico del usuario autenticado.
    """
    try:
        payment_method = PaymentMethod.objects.get(id=method_id, user=request.user)
        payment_method.delete()
        return Response({'message': 'Método de pago eliminado exitosamente.'}, status=status.HTTP_200_OK)
    except PaymentMethod.DoesNotExist:
        return Response({'error': 'Método de pago no encontrado o no pertenece al usuario.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminRole])
def create_coupon(request):
    """
    Crea un nuevo cupón.
    """
    serializer = CouponSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Cupón creado exitosamente.', 'coupon': serializer.data},
                        status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminRole])
def delete_coupon(request, coupon_id):
    """
    Elimina un cupón por su ID.
    """
    try:
        coupon = Coupon.objects.get(id=coupon_id)
        coupon.delete()
        return Response({'message': 'Cupón eliminado exitosamente.'}, status=status.HTTP_200_OK)
    except Coupon.DoesNotExist:
        return Response({'error': 'Cupón no encontrado.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminRole])
def add_coupon_to_user(request):
    """
    Asigna un cupón al usuario autenticado.
    Requiere: coupon_id
    """
    coupon_id = request.data.get('coupon_id')
    if not coupon_id:
        return Response({'error': 'Se requiere coupon_id.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        coupon = Coupon.objects.get(id=coupon_id)
        add_notifications('¡NUEVO CUPÓN', 'Pide tus productos favoritos', 'OTHER', 'CLIENT')
    except Coupon.DoesNotExist:
        return Response({'error': 'Cupón no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    coupon_user, created = CouponUser.objects.get_or_create(user=request.user, coupon=coupon)

    if not created:
        return Response({'message': 'El cupón ya está asignado al usuario.'}, status=status.HTTP_200_OK)

    serializer = CouponUserSerializer(coupon_user)
    return Response({'message': 'Cupón asignado al usuario exitosamente.', 'coupon_user': serializer.data},
                    status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminRole])
def remove_coupon_from_user(request):
    """
    Elimina un cupón específico del usuario autenticado.
    Requiere: coupon_id
    """
    coupon_id = request.data.get('coupon_id')
    if not coupon_id:
        return Response({'error': 'Se requiere coupon_id.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        coupon_user = CouponUser.objects.get(user=request.user, coupon_id=coupon_id)
        coupon_user.delete()
        return Response({'message': 'Cupón eliminado del usuario correctamente.'}, status=status.HTTP_200_OK)
    except CouponUser.DoesNotExist:
        return Response({'error': 'El cupón no está asignado al usuario.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_coupons(request):
    """
    Retorna todos los cupones asignados al usuario autenticado.
    """
    coupons_user = CouponUser.objects.filter(user=request.user)
    serializer = CouponUserSerializer(coupons_user, many=True)
    return Response({'coupons': serializer.data}, status=status.HTTP_200_OK)
