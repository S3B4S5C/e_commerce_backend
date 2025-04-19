from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.create_user, name='api-user-register'),
    path('login', views.login_user, name='api-user-login'),
    path('test-token', views.test_token, name='api-user-test-token'),
    path('requestProfile', views.query_profile, name='api-user-request-profile'),
    path('updateProfile', views.update_profile, name='api-user-update-profile'),
    path('changePassword', views.change_password, name='api-user-change-password')
]
