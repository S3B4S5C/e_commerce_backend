from django.urls import path
from . import views

urlpatterns = [
    path('coupon/create/', views.create_coupon, name='create-coupon'),
    path('coupon/delete/<uuid:coupon_id>', views.delete_coupon, name='delete-coupon'),
    path('coupon/add-to-user/', views.add_coupon_to_user, name='add-coupon-to-user'),
    path('coupon/remove-from-user/', views.remove_coupon_from_user, name='remove-coupon-from-user'),
    path('coupon/user', views.get_user_coupons, name='get-user-coupons')
]
