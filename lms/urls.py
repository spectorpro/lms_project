from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    LessonCreateAPIView,
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView,
    SubscriptionToggleAPIView,
    PaymentCreateAPIView,
    PaymentStatusAPIView,
)

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")

urlpatterns = [
    path("", include(router.urls)),
    path("lessons/create/", LessonCreateAPIView.as_view(), name="lesson-create"),
    path("lessons/", LessonListAPIView.as_view(), name="lesson-list"),
    path("lessons/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson-retrieve"),
    path("lessons/<int:pk>/update/", LessonUpdateAPIView.as_view(), name="lesson-update"),
    path("lessons/<int:pk>/delete/", LessonDestroyAPIView.as_view(), name="lesson-destroy"),
    path("subscription/toggle/", SubscriptionToggleAPIView.as_view(), name="subscription-toggle"),
    path("payments/", PaymentCreateAPIView.as_view(), name="payment-create"),
    path("payments/<int:pk>/status/", PaymentStatusAPIView.as_view(), name="payment-status"),
]