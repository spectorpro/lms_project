from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone


@shared_task
def block_inactive_users():
    """Блокирует пользователей, не заходивших более месяца.

    Выборка: last_login старше 30 дней и is_active=True.
    Обновление выполняется батчем — одним SQL-запросом update.
    Возвращает число заблокированных пользователей.
    """
    month_ago = timezone.now() - timedelta(days=30)
    User = get_user_model()

    blocked_count = User.objects.filter(
        last_login__lt=month_ago,
        is_active=True,
    ).update(is_active=False)

    return f"Заблокировано пользователей: {blocked_count}"
