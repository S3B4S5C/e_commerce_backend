from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from products.models import Product, Tag
from .models import ActivityLog
from .serializers import ActivityLogSerializer
from products.serializers import ProductSerializer, TagSerializer2
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from users.permisions import IsAdminRole


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminRole])
def get(request):
    products = Product.objects.filter(deleted_at__isnull=True)
    tags = Tag.objects.all()
    activities = ActivityLog.objects.order_by('-time')[:10]  # últimas 10 actividades

    categories = products.values('category').distinct()
    categories_data = [
        {
            'id': f'CAT{str(i+1).zfill(3)}',
            'name': c['category'],
            'description': f'Productos de la categoría {c["category"]}',
            'productCount': products.filter(category=c['category']).count()
        }
        for i, c in enumerate(categories)
    ]
    return JsonResponse({
        'products': ProductSerializer(products, many=True).data,
        'tags': TagSerializer2(tags, many=True).data,
        'categories': categories_data,
        'activities': ActivityLogSerializer(activities, many=True).data,
    }, json_dumps_params={'ensure_ascii': False})
