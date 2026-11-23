from users.models import Payment
from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from users.permissions import IsModer, IsOwner
from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer, PaymentSerializer
from .paginators import LmsPagination
from .services import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_session,
    retrieve_stripe_session,
)


from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiParameter,
    inline_serializer,
)

@extend_schema_view(
    list=extend_schema(summary="Список курсов", description="Возвращает список курсов с пагинацией.",
                       responses={200: CourseSerializer}, tags=["Курсы"]),
    create=extend_schema(summary="Создать курс",
                         description="Создает курс. Владельцем автоматически становится текущий пользователь.",
                         request=CourseSerializer, responses={201: CourseSerializer}, tags=["Курсы"]),
    retrieve=extend_schema(summary="Получить курс", description="Возвращает курс по ID.",
                           responses={200: CourseSerializer}, tags=["Курсы"]),
    update=extend_schema(summary="Обновить курс", description="Полностью обновляет курс по ID.",
                         request=CourseSerializer, responses={200: CourseSerializer}, tags=["Курсы"]),
    partial_update=extend_schema(summary="Частично обновить курс", description="Частично обновляет курс по ID.",
                                 request=CourseSerializer, responses={200: CourseSerializer}, tags=["Курсы"]),
    destroy=extend_schema(summary="Удалить курс", description="Удаляет курс по ID. Доступно только владельцу.",
                          responses={204: OpenApiResponse(description="Курс удален")}, tags=["Курсы"]),
)
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    pagination_class = LmsPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderators").exists() or user.is_superuser:
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [permissions.IsAuthenticated, ~IsModer]
        elif self.action == "destroy":
            self.permission_classes = [permissions.IsAuthenticated, IsOwner]
        else:
            self.permission_classes = [permissions.IsAuthenticated, IsModer | IsOwner]
        return [permission() for permission in self.permission_classes]


class LessonCreateAPIView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, ~IsModer]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    pagination_class = LmsPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderators").exists() or user.is_superuser:
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsModer | IsOwner]


class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsModer | IsOwner]


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]


class SubscriptionToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")

        course_item = get_object_or_404(Course, id=course_id)
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = "подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "подписка добавлена"

        return Response({"message": message})


@extend_schema(
    summary="Создать платеж",
    description=(
            "Создает запись платежа в БД и инициирует сессию оплаты в Stripe. "
            "В ответе возвращается ссылка на оплату (stripe_payment_url)."
    ),
    request=PaymentSerializer,
    responses={
        201: PaymentSerializer,
        400: OpenApiResponse(description="Ошибка валидации: не указан курс/урок или некорректная сумма"),
        401: OpenApiResponse(description="Не авторизован"),
    },
    tags=["Платежи"],
)
class PaymentCreateAPIView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)

        product_name = (
            payment.paid_course.title if payment.paid_course else payment.paid_lesson.title
        )

        payment.stripe_product_id = create_stripe_product(product_name)

        amount_cents = int(payment.amount * 100)
        payment.stripe_price_id = create_stripe_price(amount_cents, payment.stripe_product_id)

        session = create_stripe_session(payment.stripe_price_id)

        payment.stripe_session_id = session.id
        payment.stripe_payment_url = session.url

        payment.save()


@extend_schema(
    summary="Статус платежа",
    description="Получает актуальный статус оплаты из Stripe по ID сессии.",
    parameters=[
        OpenApiParameter(name="pk", type=int, location=OpenApiParameter.PATH, description="ID платежа"),
    ],
    responses={
        200: OpenApiResponse(
            response={"status": "string", "payment_status": "string", "payment_url": "string"},
            description="Текущий статус сессии и ссылка на оплату"
        ),
        404: OpenApiResponse(description="Платеж не найден"),
    },
    tags=["Платежи"],
)
class PaymentStatusAPIView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer

    def retrieve(self, request, *args, **kwargs):
        payment = self.get_object()

        if not payment.stripe_session_id:
            return Response(
                {"error": "У этого платежа нет сессии Stripe"},
                status=400
            )

        session = retrieve_stripe_session(payment.stripe_session_id)

        payment.status = session.payment_status
        payment.save(update_fields=["status"])

        return Response({
            "status": session.status,
            "payment_status": session.payment_status,
            "payment_url": payment.stripe_payment_url,
        })
