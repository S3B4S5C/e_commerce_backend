from django.urls import path
from . import views

urlpatterns = [
    path('overview', views.get, name='api-overview'),
    path('report', views.get_report, name='get-report'),
]
