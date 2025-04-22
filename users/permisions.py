# permissions.py
from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    """
    Permite el acceso solo a usuarios con rol 'ADMIN'.
    """

    def has_permission(self, request, view):
        print("Checking permission for user:", request.user)
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == 'ADMIN'
        )
