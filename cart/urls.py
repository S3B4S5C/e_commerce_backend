from django.urls import path
from . import views

urlpatterns = [
    path('delete/<uuid:cart_id>/', views.delete_cart, name='delete-cart'),
    path('addproduct', views.add_product_to_cart, name='add-product-to-cart'),
    path('removeproduct', views.remove_product_from_cart, name='remove-product-from-cart'),
    path('view', views.view_cart, name='view-cart'),
]
