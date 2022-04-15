from django.utils.translation import gettext_lazy as _

from rest_framework import permissions, exceptions

from reservations.models import Table, Reservation


class CanManageTables(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('reservations.can_manage_tables')

    def has_object_permission(self, request, view, table: Table):
        return table.can_be_deleted if request.method.lower() == 'delete' else True


class CanManageReservation(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('reservations.can_manage_reservation')

    def has_object_permission(self, request, view, reservation: Reservation):
        if request.method.lower() == 'delete' and not reservation.is_in_future:
            raise exceptions.PermissionDenied(_('You can\'t delete reservation in the past'))
        return True
