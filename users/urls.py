from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    PaymentViewSet,
    ProfileRetrieveUpdateAPIView,
    UserCreateAPIView,
    UserProfileAPIView,
)

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payments")

urlpatterns = [
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path("profile/", ProfileRetrieveUpdateAPIView.as_view(), name="profile"),
    path("profile/<int:pk>/", UserProfileAPIView.as_view(), name="user-profile"),
] + router.urls
