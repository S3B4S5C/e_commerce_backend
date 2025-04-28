from django.urls import path
from .views import VoiceAssistantView

urlpatterns = [
    path("voz/", VoiceAssistantView.as_view(), name="asistente-voz")
]
