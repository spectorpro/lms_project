from django.urls import path
from rest_framework.routers import DefaultRouter

from lms.views import SubscriptionToggleAPIView
from .views import (
    CourseViewSet,
    LessonCreateAPIView,
    LessonDestroyAPIView,
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
)

router = DefaultRouter()
router.register("courses", CourseViewSet, basename="courses")

app_name = "lms"

urlpatterns = [
    path("lessons/", LessonListAPIView.as_view(), name="lesson-list"),
    path("lessons/create/", LessonCreateAPIView.as_view(), name="lesson-create"),
    path("lessons/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson-retrieve"),
    path("lessons/<int:pk>/update/", LessonUpdateAPIView.as_view(), name="lesson-update"),
    path("lessons/<int:pk>/delete/", LessonDestroyAPIView.as_view(), name="lesson-delete"),
    path("subscriptions/", SubscriptionToggleAPIView.as_view(), name="subscription-toggle"),
] + router.urls
