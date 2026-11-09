from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProfileUpdateAPIView, PaymentViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payments')

urlpatterns = [
    path('profile/', ProfileUpdateAPIView.as_view(), name='profile'),
] + router.urls