from rest_framework import generics, permissions, viewsets

from .models import User, Payment
from .serializers import (
    PaymentSerializer,
    UserPublicSerializer,
    UserRegisterSerializer,
    UserSerializer,
)


class UserCreateAPIView(generics.CreateAPIView):
    """Регистрация — открыта для всех."""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Свой профиль: просмотр и редактирование, только по токену."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileAPIView(generics.RetrieveAPIView):
    """Чужой профиль: только общая информация (без пароля, фамилии, платежей)."""
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.get_object() == self.request.user:
            return UserSerializer
        return UserPublicSerializer


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """История только своих платежей."""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
