from rest_framework import permissions
from api.models import UserRole

MODERATOR_METHODS = ('PATCH', 'DELETE')


class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               request.user.role == UserRole.ADMIN or request.user.is_superuser


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or \
               request.user.is_authenticated and \
               request.user.role == UserRole.ADMIN or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or \
               request.user.is_authenticated and \
               request.user.role == UserRole.ADMIN or request.user.is_superuser


class IsAuthorOrModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or \
               request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.method in MODERATOR_METHODS \
               and request.user.role == UserRole.MODERATOR or \
               obj.author == request.user
