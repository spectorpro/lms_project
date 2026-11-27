from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Course, Subscription


@shared_task
def send_course_update_emails(course_id):
    """Рассылает письма всем подписчикам курса об обновлении материалов.

    Принимает ID курса, который только что был обновлен.
    Возвращает количество отправленных писем.
    """
    course = Course.objects.filter(id=course_id).first()
    if not course:
        return "Курс не найден"

    emails = (
        Subscription.objects.filter(course=course)
        .values_list("user__email", flat=True)
        .distinct()
    )

    sent_count = 0
    for email in emails:
        send_mail(
            subject=f"Обновление курса: {course.title}",
            message=(
                f"Здравствуйте!\n\n"
                f"Материалы курса «{course.title}» были обновлены.\n"
                f"Загляните и посмотрите, что нового.\n\n"
                f"С уважением,\nкоманда онлайн-школы"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        sent_count += 1

    return f"Отправлено писем: {sent_count} по курсу «{course.title}»"
