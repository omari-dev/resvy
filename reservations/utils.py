import itertools

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def present_or_future_date(value):
    if value < timezone.now().today():
        raise ValidationError(_('The date cannot be in the past'))
    return value


def present_or_future_time(value):
    if value < timezone.now().time():
        raise ValidationError(_('The time cannot be in the past'))
    return value


def is_time_during_working_hour(time):
    return settings.RESERVATION_STARTING_FROM_TIME < time < settings.RESERVATION_ENDS_AT_TIME


def get_start_reservation_time(time):
    return time if is_time_during_working_hour(time) else settings.RESERVATION_STARTING_FROM_TIME


def split_list_to_check(lst, chunk_size=2):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def check_availability_for_table(table):
    from reservations.models import Reservation
    time = timezone.now().time()
    start_time = get_start_reservation_time(time)

    end_time = settings.RESERVATION_ENDS_AT_TIME
    today_reservations = Reservation.objects.today().on_table(table).upcoming().values_list('from_time', 'to_time')
    fake_reservation = (end_time, start_time)

    # Todo: handle below two edge cases in more propre way
    if not today_reservations:
        # Handle no reservation
        return [(start_time, end_time)]

    if today_reservations[0] == tuple(reversed(fake_reservation)):
        # Handle one reservation for the whole day
        return []

    slot_entries = sorted(itertools.chain(fake_reservation, *today_reservations))
    return split_list_to_check(slot_entries)


def get_fit_table_size(persons):
    from reservations.models import Table

    fit_table = Table.objects.filter(number_of_seats__gte=persons).distinct('number_of_seats')[:1]
    if not fit_table:
        return
    return fit_table[0].number_of_seats
