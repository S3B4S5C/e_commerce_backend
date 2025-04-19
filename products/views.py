from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Product, Tag, ProductReview, FavoriteProduct, Tagged
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import Random


@api_view(['POST'])
def register_product(request):
    """
    Crea un nuevo producto
    """
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save()
        return Response({
            'message': 'Producto creado correctamente',
            'product': ProductSerializer(product).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def product_list(request):
    products = Product.objects.filter(deleted_at__isnull=True)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_product_categories(request):
    """
    Devuelve todas las categorías únicas de productos que no han sido eliminados.
    """
    categories = Product.objects.filter(deleted_at__isnull=True).values_list('category', flat=True).distinct()
    return Response({'categories': list(categories)}, status=status.HTTP_200_OK)


@api_view(['GET'])
def search_products(request):
    """
    Buscar productos con filtros opcionales:
    - name (nombre del producto)
    - category (categoría del producto)
    - brand (marca)
    - min_price (precio mínimo)
    - max_price (precio máximo)
    """
    name = request.GET.get('name', '')
    category = request.GET.get('category', '')
    brand = request.GET.get('brand', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    filters = Q(deleted_at__isnull=True)

    if name:
        filters &= Q(name__icontains=name)
    if category:
        filters &= Q(category__icontains=category)
    if brand:
        filters &= Q(brand__icontains=brand)
    if min_price:
        filters &= Q(price__gte=min_price)
    if max_price:
        filters &= Q(price__lte=max_price)

    products = Product.objects.filter(filters)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_tag(request):
    name = request.data.get('name')
    if not name:
        return Response({'error': 'El nombre del tag es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
    tag = Tag.objects.create(name=name)
    return Response({'message': 'Tag creado correctamente', 'tag': {'id': str(tag.id), 'name': tag.name}}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def delete_tag(request, tag_id):
    try:
        tag = Tag.objects.get(id=tag_id)
        tag.delete()
        return Response({'message': 'Tag eliminado correctamente'}, status=status.HTTP_200_OK)
    except Tag.DoesNotExist:
        return Response({'error': 'Tag no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def create_review(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    rating = request.data.get('rating')
    comment = request.data.get('comment', '')

    if not rating:
        return Response({'error': 'El campo rating es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        review = ProductReview.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )
        review.clean()
        review.save()
        return Response({'message': 'Reseña creada correctamente'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_review(request, review_id):
    try:
        review = ProductReview.objects.get(id=review_id, user=request.user)
        review.delete()
        return Response({'message': 'Reseña eliminada correctamente'}, status=status.HTTP_200_OK)
    except ProductReview.DoesNotExist:
        return Response({'error': 'Reseña no encontrada o no autorizada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def add_to_favorites(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        fav, created = FavoriteProduct.objects.get_or_create(user=request.user, product=product)
        if created:
            return Response({'message': 'Producto añadido a favoritos'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'El producto ya estaba en favoritos'}, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def remove_from_favorites(request, product_id):
    try:
        favorite = FavoriteProduct.objects.get(user=request.user, product_id=product_id)
        favorite.delete()
        return Response({'message': 'Producto eliminado de favoritos'}, status=status.HTTP_200_OK)
    except FavoriteProduct.DoesNotExist:
        return Response({'error': 'El producto no estaba en favoritos'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def associate_tag_to_product(request):
    product_id = request.data.get('product_id')
    tag_id = request.data.get('tag_id')

    if not product_id or not tag_id:
        return Response({'error': 'Faltan parámetros (product_id y tag_id)'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id)
        tag = Tag.objects.get(id=tag_id)
        tagged, created = Tagged.objects.get_or_create(product=product, tag=tag)
        if created:
            return Response({'message': 'Tag asociado al producto correctamente'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'El tag ya estaba asociado a este producto'}, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Tag.DoesNotExist:
        return Response({'error': 'Tag no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def remove_tag_from_product(request):
    product_id = request.data.get('product_id')
    tag_id = request.data.get('tag_id')

    if not product_id or not tag_id:
        return Response({'error': 'Faltan parámetros (product_id y tag_id)'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        tagged = Tagged.objects.get(product_id=product_id, tag_id=tag_id)
        tagged.delete()
        return Response({'message': 'Tag desasociado del producto correctamente'}, status=status.HTTP_200_OK)
    except Tagged.DoesNotExist:
        return Response({'error': 'La relación entre producto y tag no existe'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_tags_for_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        tags = Tag.objects.filter(tagged__product=product).values('id', 'name')
        return Response({'product': str(product.id), 'tags': list(tags)}, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_product(request, product_id):
    """
    Elimina un producto (soft delete si deseas).
    """
    try:
        product = Product.objects.get(id=product_id)
        product.deleted_at = timezone.now()
        product.save()
        return Response({'message': 'Producto eliminado correctamente'}, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def update_product(request, product_id):
    """
    Actualiza los datos de un producto.
    """
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Producto actualizado correctamente', 'product': serializer.data}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_favorite_products(request):
    """
    Devuelve todos los productos que el usuario autenticado ha marcado como favoritos.
    """
    favorites = FavoriteProduct.objects.filter(user=request.user).select_related('product')
    products = [fav.product for fav in favorites]
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_most_favorited_products(request):
    """
    Devuelve los productos ordenados por la cantidad de veces que fueron marcados como favoritos.
    """
    products = Product.objects.filter(deleted_at__isnull=True) \
        .annotate(favorite_count=Count('favoriteproduct')) \
        .order_by('-favorite_count')

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_random_product(request):
    """
    Devuelve 4 productos aleatorios que no han sido eliminados (DB-level).
    """
    products = Product.objects.filter(deleted_at__isnull=True).order_by(Random())[:4]
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
