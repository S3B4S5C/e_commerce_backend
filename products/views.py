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
from .recomendation import recommend_products, recommend_global_based_on_product
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from logs.utils import get_client_ip
from logs.models import ActivityLog
from users.permisions import IsAdminRole


@api_view(['POST'])
def register_product(request):
    """
    Crea un nuevo producto
    """
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save()
        ip = get_client_ip(request)
        ActivityLog.objects.create(
            type='product',
            user=request.user,
            description='Se agrego un nuevo producto',
            entity_id=product.id,
            ip_address=ip
        )
        return Response({
            'message': 'Producto creado correctamente',
            'product': ProductSerializer(product).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def cors_test(request):
    return JsonResponse({"message": "CORS working!"})


@api_view(['GET'])
def product_list(request):
    print('Hola')
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


@api_view(['GET'])
def search_product(request):
    """
    Buscar productos con filtros opcionales:
    - q (búsqueda general en name, category y brand)
    - ordering (campo para ordenar: name, category, brand. Agregar '-' para descendente)
    """
    query = request.GET.get('q', '')
    ordering = request.GET.get('ordering', 'name')  # Por defecto ordena por nombre ascendente

    filters = Q(deleted_at__isnull=True)

    if query:
        filters &= (
            Q(name__icontains=query) |
            Q(category__icontains=query) |
            Q(brand__icontains=query)
        )

    allowed_orderings = ['name', '-name', 'category', '-category', 'brand', '-brand']
    if ordering not in allowed_orderings:
        ordering = 'name'

    products = Product.objects.filter(filters).order_by(ordering)
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


@api_view(['GET'])
def get_product_by_id(request, product_id):
    """
    Retorna la información de un producto dado su ID.
    """
    try:
        product = Product.objects.get(id=product_id)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
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
            ip = get_client_ip(request)
            ActivityLog.objects.create(
                type='tag',
                user=request.user,
                description='Se agrego un tag a un producto',
                entity_id=product.id,
                ip_address=ip
                )
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
        ip = get_client_ip(request)
        ActivityLog.objects.create(
            type='tag',
            user=request.user,
            description='Se agrego un tag a un producto',
            entity_id=tag_id.id,
            ip_address=ip
                )
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
        ip = get_client_ip(request)
        ActivityLog.objects.create(
            type='product',
            user=request.user,
            description='Se elimino un producto',
            entity_id=product.id,
            ip_address=ip
        )
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
        ip = get_client_ip(request)
        ActivityLog.objects.create(
            type='product',
            user=request.user,
            description='Se actualizó',
            entity_id=product.id,
            ip_address=ip
        )
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


@api_view(['GET'])
def get_recommendations(request):
    try:
        # Obtener IDs de productos recomendados
        recommended_ids = recommend_products()

        # Obtener productos desde la base de datos (manteniendo el orden)
        products = list(Product.objects.filter(id__in=recommended_ids, deleted_at__isnull=True))
        products_sorted = sorted(products, key=lambda p: recommended_ids.index(str(p.id)))

        # Serializar
        serializer = ProductSerializer(products_sorted, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations_cart(request, product_id):
    """
    Agrega un producto al carrito y devuelve recomendaciones basadas en IA colectiva.
    Espera: { "product_id": 123 }
    """

    if not product_id:
        return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    # Obtener recomendaciones basadas en el producto
    recommended_ids = recommend_global_based_on_product(product.id)
    recommended_products = Product.objects.filter(id__in=recommended_ids)

    serialized_recommendations = ProductSerializer(recommended_products, many=True)

    return Response({
        "message": "Product added to cart.",
        "recommended_products": serialized_recommendations.data
    }, status=status.HTTP_200_OK)
