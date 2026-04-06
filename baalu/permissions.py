from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает чтение всем, но изменение/удаление — только админам.
    """

    def has_permission(self, request, view):
        # Если метод "безопасный" (GET, HEAD, OPTIONS), пускаем всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # В противном случае (POST, PUT, DELETE) проверяем, что юзер — админ
        return bool(request.user and request.user.is_staff)