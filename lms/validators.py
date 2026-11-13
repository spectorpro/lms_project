from urllib.parse import urlparse

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

ALLOWED_HOSTS = {"youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"}


def validate_video_url(value):
    """Функция-валидатор: разрешаем только ссылки на youtube.com."""
    if not value:
        return

    try:
        parsed = urlparse(value)
    except ValueError:
        raise ValidationError("Некорректный URL.")

    host = (parsed.hostname or "").lower()

    if host not in ALLOWED_HOSTS:
        raise ValidationError(
            f"Разрешены только ссылки на youtube.com, получено: {host or 'пустой адрес'}"
        )


class VideoUrlValidator:
    """Класс-валидатор для использования в Meta сериализатора."""

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        validate_video_url(value.get(self.field))

    def __eq__(self, other):
        return isinstance(other, VideoUrlValidator) and self.field == other.field
