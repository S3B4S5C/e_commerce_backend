from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from products.models import Product, Tag, Stock
from orders.models import Order, OrderItem
from users.models import UserAccount
from .models import ActivityLog
from .serializers import ActivityLogSerializer
from products.serializers import ProductSerializer, TagSerializer2
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from users.permisions import IsAdminRole
from datetime import datetime
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminRole])
def get(request):
    products = Product.objects.filter(deleted_at__isnull=True)
    tags = Tag.objects.all()
    activities = ActivityLog.objects.order_by('-time')[:10]

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminRole])
def get_report(request):
    hoy = datetime.today()
    primer_dia_mes = hoy.replace(day=1)

    total_productos = Product.objects.filter(deleted_at__isnull=True).count()

    productos_mas_vendidos = (
        OrderItem.objects
        .values('product__name')
        .annotate(total_vendidos=Sum('quantity'))
        .order_by('-total_vendidos')[:5]
    )

    productos_bajo_stock = (
        Stock.objects
        .filter(quantity__lt=10)
        .values('product__name', 'quantity')
    )

    productos_recientes = (
        Product.objects
        .filter(created_at__gte=primer_dia_mes, deleted_at__isnull=True)
        .values('name', 'created_at')
    )

    total_pedidos = Order.objects.filter(deleted_at__isnull=True).count()

    ingresos_totales = (
        Order.objects
        .filter(deleted_at__isnull=True)
        .aggregate(total=Sum('total_price'))['total'] or 0
    )

    total_usuarios = UserAccount.objects.count()

    nuevos_usuarios_mes = UserAccount.objects.filter(created_at__gte=primer_dia_mes).count()

    ventas_por_mes = (
        Order.objects
        .filter(deleted_at__isnull=True)
        .annotate(mes=TruncMonth('created_at'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    usuarios_por_mes = (
        UserAccount.objects
        .annotate(mes=TruncMonth('created_at'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    productos_por_categoria = (
        OrderItem.objects
        .values('product__category')
        .annotate(total_vendidos=Sum('quantity'))
        .order_by('-total_vendidos')
    )

    return Response({
        'total_productos': total_productos,
        'productos_mas_vendidos': list(productos_mas_vendidos),
        'productos_bajo_stock': list(productos_bajo_stock),
        'productos_recientes': list(productos_recientes),
        'total_pedidos': total_pedidos,
        'ingresos_totales': ingresos_totales,
        'total_usuarios': total_usuarios,
        'nuevos_usuarios_mes': nuevos_usuarios_mes,
        'ventas_por_mes': list(ventas_por_mes),
        'usuarios_por_mes': list(usuarios_por_mes),
        'productos_vendidos_por_categoria': list(productos_por_categoria),
    })
