from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    LessonCreateAPIView,
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView,
)

router = DefaultRouter()
router.register("courses", CourseViewSet)

urlpatterns = [
    path("", include(router.urls)),  # api/courses/ и api/courses/{id}/
    path("lessons/", LessonListAPIView.as_view()),          # GET — список уроков
    path("lessons/create/", LessonCreateAPIView.as_view()), # POST — создание
    path("lessons/<int:pk>/", LessonRetrieveAPIView.as_view()),   # GET — один урок
    path("lessons/<int:pk>/update/", LessonUpdateAPIView.as_view()),  # PUT/PATCH
    path("lessons/<int:pk>/delete/", LessonDestroyAPIView.as_view()), # DELETE
]
