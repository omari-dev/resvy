from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .filters import ReservationDateFilter
from .models import Table, Reservation
from .permissions import CanManageTables, CanManageReservation
from .serializers import TableSerializer, ReservationSerializer, TableAvailabilitySerializer
from .utils import get_fit_table_size, openapi_ready


class TableView(mixins.ListModelMixin, mixins.DestroyModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = TableSerializer
    permission_classes = (IsAuthenticated, CanManageTables)
    queryset = Table.objects.all()

    @extend_schema(parameters=[OpenApiParameter(name="number_of_persons", required=True, type=int), ], )
    @action(detail=False, url_name='availability', serializer_class=TableAvailabilitySerializer, )
    def availability(self, request: Request):
        number_of_persons = request.query_params.get('number_of_persons', 'invalid')
        if not number_of_persons.isdigit():
            return Response(_('Only digits are acceptable'), status=status.HTTP_400_BAD_REQUEST)

        if not Table.objects.filter(number_of_seats__gte=number_of_persons).exists():
            return Response(_('There are no tables fit this number on one table'), status=status.HTTP_400_BAD_REQUEST)

        fit_table_size = get_fit_table_size(number_of_persons)
        tables = Table.objects.filter(number_of_seats=fit_table_size)
        serializer = self.get_serializer(instance=tables, many=True)
        return Response(serializer.data)


class ReservationView(mixins.ListModelMixin, mixins.DestroyModelMixin,  mixins.CreateModelMixin, GenericViewSet):
    serializer_class = ReservationSerializer
    queryset = Reservation.objects.all()
    permission_classes = (IsAuthenticated, CanManageReservation)
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filter_class = ReservationDateFilter
    ordering_fields = ['from_time', 'to_time']
    ordering = ['from_time', ]

    @openapi_ready
    def get_queryset(self):
        queryset = Reservation.objects.all()
        if self.request.user.is_employee:
            queryset = queryset.today()
        elif self.request.user.is_admin and self.request.query_params.get('all', 'false').lower() == 'false':
            queryset = queryset.today()
        return queryset

    @extend_schema(parameters=[OpenApiParameter(name="all", required=False, type=bool, default=False), ], )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
