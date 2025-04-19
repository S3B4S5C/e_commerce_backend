from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_cart, name='create-cart'),
    path('delete/<uuid:cart_id>/', views.delete_cart, name='delete-cart'),
    path('addproduct', views.add_product_to_cart, name='add-product-to-cart'),
    path('removeproduct', views.remove_product_from_cart, name='remove-product-from-cart'),
    path('view/<uuid:cart_id>', views.view_cart, name='view-cart'),
]
