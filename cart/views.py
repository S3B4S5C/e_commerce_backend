from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product
from decimal import Decimal


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_cart(request):
    """
    Crea un nuevo carrito para el usuario autenticado.
    """
    data = request.data.copy()
    data['user'] = request.user.id
    serializer = CartSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Carrito creado exitosamente',
            'cart': serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cart(request, cart_id):
    """
    Elimina (lógicamente) un carrito del usuario autenticado.
    """
    try:
        cart = Cart.objects.get(id=cart_id, user=request.user)

        if cart.deleted_at is not None:
            return Response({'message': 'El carrito ya fue eliminado.'}, status=status.HTTP_400_BAD_REQUEST)

        cart.deleted_at = timezone.now()
        cart.save()
        return Response({'message': 'Carrito eliminado exitosamente.'}, status=status.HTTP_200_OK)

    except Cart.DoesNotExist:
        return Response({'error': 'Carrito no encontrado.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product_to_cart(request):
    """
    Agrega un producto al carrito del usuario autenticado.
    Requiere: cart_id, product_id, quantity_product
    """
    cart_id = request.data.get('cart_id')
    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity_product', 1))

    if not cart_id or not product_id:
        return Response({'error': 'cart_id y product_id son obligatorios.'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        cart = Cart.objects.get(id=cart_id, user=request.user, deleted_at__isnull=True)
    except Cart.DoesNotExist:
        return Response({'error': 'Carrito no encontrado o eliminado.'},
                        status=status.HTTP_404_NOT_FOUND)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado.'},
                        status=status.HTTP_404_NOT_FOUND)

    # Verificar si el producto ya está en el carrito
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        cart_item.quantity_product = quantity
    else:
        cart_item.quantity_product += quantity

    cart_item.save()

    # Actualizar el total del carrito
    cart.total_price += Decimal(str(product.price)) * Decimal(str(quantity))
    cart.save()

    serializer = CartItemSerializer(cart_item)
    return Response({
        'message': 'Producto agregado al carrito exitosamente.',
        'item': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_product_from_cart(request):
    """
    Elimina un producto específico del carrito del usuario autenticado.
    Requiere: cart_id, product_id
    """
    cart_id = request.data.get('cart_id')
    product_id = request.data.get('product_id')

    if not cart_id or not product_id:
        return Response({'error': 'cart_id y product_id son obligatorios.'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        cart = Cart.objects.get(id=cart_id, user=request.user, deleted_at__isnull=True)
    except Cart.DoesNotExist:
        return Response({'error': 'Carrito no encontrado o eliminado.'},
                        status=status.HTTP_404_NOT_FOUND)

    try:
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
    except CartItem.DoesNotExist:
        return Response({'error': 'Producto no encontrado en el carrito.'},
                        status=status.HTTP_404_NOT_FOUND)

    # Actualizar el total del carrito antes de eliminar
    product = cart_item.product
    total_to_subtract = Decimal(str(product.price)) * cart_item.quantity_product
    cart.total_price -= total_to_subtract
    cart.total_price = max(cart.total_price, 0)  # Asegura que no sea negativo
    cart.save()

    cart_item.delete()

    return Response({'message': 'Producto eliminado del carrito correctamente.'},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_cart(request, cart_id):
    """
    Muestra el contenido del carrito con los productos y cantidades.
    """
    try:
        cart = Cart.objects.get(id=cart_id, user=request.user, deleted_at__isnull=True)
    except Cart.DoesNotExist:
        return Response({'error': 'Carrito no encontrado o eliminado.'}, status=status.HTTP_404_NOT_FOUND)

    cart_data = CartSerializer(cart).data
    cart_items = CartItem.objects.filter(cart=cart)
    cart_items_data = CartItemSerializer(cart_items, many=True).data

    return Response({
        'cart': cart_data,
        'items': cart_items_data
    }, status=status.HTTP_200_OK)
