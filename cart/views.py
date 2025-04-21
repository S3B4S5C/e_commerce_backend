from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product
from decimal import Decimal
from products.serializers import ProductSerializer

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
    Si no hay un carrito activo (deleted_at=None), se crea uno nuevo.
    Requiere: product_id, quantity_product
    """
    user = request.user
    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity_product', 1))

    if not product_id:
        return Response({'error': 'product_id es obligatorio.'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado.'},
                        status=status.HTTP_404_NOT_FOUND)

    cart = Cart.objects.filter(user=user, deleted_at__isnull=True).first()

    if not cart:
        cart = Cart.objects.create(user=user, total_price=0)

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
        'item': serializer.data,
        'cart_id': cart.id
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
def view_cart(request):
    """
    Retorna los productos en el carrito del usuario autenticado con su cantidad.
    """
    user = request.user

    try:
        cart = Cart.objects.get(user=user, deleted_at__isnull=True)
    except Cart.DoesNotExist:
        return Response({'error': 'No hay un carrito activo para este usuario.'},
                        status=status.HTTP_404_NOT_FOUND)

    cart_items = CartItem.objects.filter(cart=cart).select_related('product')
    
    # Retornar una lista de productos con cantidad
    products_with_quantity = []
    for item in cart_items:
        product_data = ProductSerializer(item.product).data
        product_data['quantity'] = item.quantity_product
        products_with_quantity.append(product_data)

    return Response({
        'products': products_with_quantity
    }, status=status.HTTP_200_OK)
