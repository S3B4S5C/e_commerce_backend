from django.urls import path
from . import views

urlpatterns = [
    path('realizarpedido', views.create_order, name='realizar-pedido'),
    path('payment', views.create_order_with_payment, name='stripe-payment'),
    path('payment/add', views.add_payment_method, name='add-payment-method'),
    path('payment/delete/<uuid:payment_id>', views.delete_payment_method, name='delete-payment-method'),
    path('confirm-payment/<str:payment_id>/', views.confirmar_pago, name='confirm_payment'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('shipping/create/', views.create_shipping_method, name='create_shipping_method'),
    path('shipping/delete/<uuid:method_id>', views.delete_shipping_method, name='delete_shipping_method'),
    path('shipping/list', views.list_shipping_methods, name='list_shipping_methods'),
    path('status/create/', views.create_order_status, name='crear_estado'),
    path('status/delete/<str:name>', views.delete_order_status, name='eliminar_estado'),
    path('', views.mis_ordenes, name='mis_ordenes'),
]
