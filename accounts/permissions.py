from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import UserRole


class IsAuthenticatedAndCustomerRole(BasePermission):
    """
    Customer = any authenticated non-admin user (per labs).
    """

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and getattr(user, "role", None) != UserRole.ADMIN)


class IsAdminUserRole(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and getattr(user, "role", None) == UserRole.ADMIN)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and getattr(user, "role", None) == UserRole.ADMIN)

