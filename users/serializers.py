from rest_framework import serializers
from lms.serializers import CourseSerializer, LessonSerializer
from .models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class PaymentHistorySerializer(serializers.ModelSerializer):
    paid_course = CourseSerializer(read_only=True)
    paid_lesson = LessonSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'payment_date', 'paid_course', 'paid_lesson',
                  'amount', 'payment_method')


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentHistorySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name',
                  'phone', 'city', 'avatar', 'payments')