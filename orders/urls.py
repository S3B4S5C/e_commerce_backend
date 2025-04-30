from django.urls import path
from . import views

urlpatterns = [
    path('payment', views.create_order_with_payment, name='stripe-payment'),
    path('confirm-payment/<str:payment_id>/', views.confirmar_pago, name='confirm_payment'),
    path('shipping/create', views.create_shipping_method, name='create_shipping_method'),
    path('shipping/delete/<uuid:method_id>', views.delete_shipping_method, name='delete_shipping_method'),
    path('shipping/list', views.list_shipping_methods, name='list_shipping_methods'),
    path('status/create', views.create_order_status, name='crear_estado'),
    path('status/delete/<str:name>', views.delete_order_status, name='eliminar_estado'),
    path('', views.mis_ordenes, name='mis_ordenes'),
]
