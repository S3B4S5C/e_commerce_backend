from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.create_user, name='api-user-register'),
    path('login', views.login_user, name='api-user-login'),
    path('test-token', views.test_token, name='api-user-login'),
]