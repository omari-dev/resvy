from django.forms import DateInput
from django_filters import DateFilter
from django_filters.rest_framework import FilterSet

from .models import Reservation


class ReservationDateFilter(FilterSet):
    from_time = DateFilter(lookup_expr="gte", widget=DateInput(attrs={'type': 'date'}))
    to_time = DateFilter(lookup_expr="lte", widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Reservation
        fields = 'from_time', 'to_time', 'table'
