from rest_framework import permissions

from reservations.models import Table, Reservation


class CanManageTables(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('reservations.can_manage_tables')

    def has_object_permission(self, request, view, table: Table):
        return table.can_be_deleted


class CanManageReservation(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('reservations.can_manage_reservation')

    def has_object_permission(self, request, view, reservation: Reservation):
        return reservation.can_be_deleted
