from users.models import Payment
from rest_framework import serializers
from .models import Course, Lesson, Subscription
from lms.validators import validate_video_url, VideoUrlValidator
from lms.models import Subscription



class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [VideoUrlValidator(field="video_url")]


class CourseSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()   # ← строка 1

    class Meta:
        model = Course
        fields = "__all__"

    def get_is_subscribed(self, obj):                     # ← строка 2
        user = self.context.get("request").user if self.context.get("request") else None
        if user is None or user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, course=obj).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "user", "payment_date", "paid_course", "paid_lesson",
            "amount", "payment_method",  # ← обрати внимание: payment_method, а не method
            "stripe_product_id", "stripe_price_id", "stripe_session_id",
            "stripe_payment_url", "status",
        ]
        read_only_fields = [
            "user", "payment_date",
            "stripe_product_id", "stripe_price_id", "stripe_session_id",
            "stripe_payment_url", "status",
        ]

    def validate(self, data):
        if not data.get("paid_course") and not data.get("paid_lesson"):
            raise serializers.ValidationError("Укажите курс или урок для оплаты")
        return data
