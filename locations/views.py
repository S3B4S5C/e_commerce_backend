from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import AddressSerializer
from .models import AddressUser, Branch
from django.utils import timezone
from products.models import Product, Stock
from logs.utils import get_client_ip
from logs.models import ActivityLog
from users.models import UserAccount


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_address(request):
    """
    Crea una dirección con coordenadas y la asocia al usuario autenticado.
    """
    serializer = AddressSerializer(data=request.data)
    if serializer.is_valid():
        address = serializer.save()
        AddressUser.objects.create(user=request.user, address=address)
        return Response({'message': 'Dirección creada exitosamente'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_addresses(request):
    """
    Obtener todas las direcciones del usuario autenticado.
    """
    user = request.user
    address_user_entries = AddressUser.objects.filter(user=user).select_related('address__coordinate')
    addresses = [entry.address for entry in address_user_entries]
    serializer = AddressSerializer(addresses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_address(request, address_id):
    """
    Eliminar una dirección específica del usuario autenticado.
    """
    user = request.user
    try:
        address_user = AddressUser.objects.get(user=user, address_id=address_id)

        address = address_user.address
        coordinate = address.coordinate
        address_user.delete()

        address.delete()
        coordinate.delete()

        return Response({'message': 'Dirección eliminada correctamente'}, status=status.HTTP_200_OK)

    except AddressUser.DoesNotExist:
        return Response({'error': 'La dirección no está asociada a este usuario'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def register_branch(request):
    """
    Crea una nueva sucursal con su dirección y coordenadas (usando serializers).
    """
    address_data = request.data.get('address')
    name = request.data.get('name')

    if not address_data or not name:
        return Response({'error': 'Los campos "name" y "address" son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

    address_serializer = AddressSerializer(data=address_data)
    if address_serializer.is_valid():
        address = address_serializer.save()
        branch = Branch.objects.create(name=name, address=address)
        return Response({
            'message': 'Sucursal registrada correctamente',
            'branch_id': str(branch.id),
            'address': AddressSerializer(address).data
        }, status=status.HTTP_201_CREATED)
    else:
        return Response(address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_branch(request, branch_id):
    """
    Elimina una sucursal (soft delete).
    """
    try:
        branch = Branch.objects.get(id=branch_id, deleted_at__isnull=True)
        branch.deleted_at = timezone.now()
        branch.save()
        return Response({'message': 'Sucursal eliminada correctamente'}, status=status.HTTP_200_OK)
    except Branch.DoesNotExist:
        return Response({'error': 'Sucursal no encontrada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def stock_by_branch(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        stock_data = Stock.objects.filter(product=product).select_related('branch')

        result = [
            {
                'branch_id': str(stock.branch.id),
                'branch_name': stock.branch.name,
                'quantity': stock.quantity
            }
            for stock in stock_data
        ]

        return Response({'product': str(product.id), 'stock_by_branch': result}, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_stock(request):
    print(request.data)
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity')

    if not product_id or quantity is None:
        return Response({'error': 'Faltan parámetros (product_id, quantity)'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return Response({'error': 'Quantity debe ser un número válido'}, status=400)

    try:
        stock = Stock.objects.create(product_id=product_id, quantity=quantity)
        ip = get_client_ip(request)
        # Asegura que user sea instancia de UserAccount
        user = request.user
        if not isinstance(user, UserAccount):
            user = UserAccount.objects.get(id=user.id)

        ActivityLog.objects.create(
            user=user,
            description=f'Se añadió stock de {quantity} para el producto con ID {product_id}',
            type='stock',
            entity_id=stock.id,
            ip_address=ip
        )

        return Response({'message': 'Stock actualizado correctamente'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
