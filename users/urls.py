from django.urls import path
from .views import ProfileUpdateAPIView

urlpatterns = [
    path("<int:pk>/update_profile/", ProfileUpdateAPIView.as_view()),
]
