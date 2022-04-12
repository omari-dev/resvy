from rest_framework import permissions


class CanAddEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('users.can_add_employee')
