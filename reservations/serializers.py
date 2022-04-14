from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Table, Reservation
from .utils import check_availability_for_table, get_fit_table_size


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ('id', 'number', 'number_of_seats')


class TableAvailabilitySerializer(serializers.ModelSerializer):
    availability = serializers.SerializerMethodField()
    for_date = serializers.DateField(default=timezone.now().date())

    class Meta:
        model = Table
        fields = ('id', 'number', 'number_of_seats', 'for_date', 'availability')

    @classmethod
    def _format_string_time(cls, string_time):
        return string_time.strftime("%I:%M %p")

    def get_availability(self, table: Table):
        slots = check_availability_for_table(table)
        formatted_slots = []
        # Todo: find proper way to form time
        for slot in slots:
            formatted_slots.append(map(lambda t: self._format_string_time(t), slot))
        return formatted_slots


class ReservationSerializer(serializers.ModelSerializer):
    table = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all())

    class Meta:
        model = Reservation
        fields = ('id', 'from_time', 'to_time', 'table', 'persons')

    def validate(self, attrs):
        from_time = attrs.get('from_time')
        to_time = attrs.get('to_time')
        persons = attrs.get('persons')
        table: Table = attrs.get('table')
        valid_duration = False

        if from_time > to_time:
            raise serializers.ValidationError(_('Invalid from_time and to_time'))

        if table.number_of_seats != get_fit_table_size(persons):
            raise serializers.ValidationError(_('This table can not accept this number of customers'))

        # todo: make check_availability_for_table return hash for each time slot to avoid this ugly for loop
        for slot in check_availability_for_table(table=attrs.get('table')):
            # todo: no need to go thorough each time slot since time slots are ordered
            if (slot[1] > from_time > slot[0]) and (slot[1] > to_time > slot[0]):
                valid_duration = True
                break

        if not valid_duration:
            raise serializers.ValidationError(_('Invalid dates'))

        return attrs

    def create(self, validated_data):
        validated_data.update(date=timezone.now().date())
        return super().create(validated_data)
