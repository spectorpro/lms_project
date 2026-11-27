from rest_framework.permissions import BasePermission


class IsModer(BasePermission):
    """Пользователь состоит в группе модераторов."""
    message = "Доступно только модераторам."

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moderators").exists()


class IsOwner(BasePermission):
    """Владелец объекта (проверка на уровне конкретного объекта)."""
    message = "Доступно только владельцу."

    def has_object_permission(self, request, view, obj):
        return obj == request.user or getattr(obj, "owner", None) == request.user
