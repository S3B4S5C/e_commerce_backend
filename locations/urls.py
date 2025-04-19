from django.urls import path
from . import views

urlpatterns = [
    path('registerAddress', views.register_address, name='api-address-register-address'),
    path('getAddress', views.get_addresses, name='api-address-get-address'),
    path('deleteAddress/<uuid:address_id>', views.delete_address, name='api-address-delete-address'),
    path('branches/register', views.register_branch, name='register-branch'),
    path('branches/<uuid:branch_id>/delete', views.delete_branch, name='delete-branch'),
    path('stock/update', views.update_stock, name='update-stock'),
    path('products/<uuid:product_id>/stock', views.stock_by_branch, name='stock-branch'),
]
