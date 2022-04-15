from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from reservations.utils import present_or_future_date, present_or_future_time


class Table(models.Model):
    number = models.PositiveIntegerField(_('Table Number'), unique=True, blank=False, null=False)
    number_of_seats = models.PositiveIntegerField(_('Number of seats'),
                                                  unique=False,
                                                  blank=False,
                                                  null=True,
                                                  validators=(MinValueValidator(1), MaxValueValidator(12)),)

    class Meta:
        permissions = (
            ('can_manage_tables', 'Can manage Tables'),
        )

    def __str__(self) -> str:
        return f'Table number: {self.number}, Number of seats: {self.number_of_seats}'

    @property
    def can_be_deleted(self) -> bool:
        return not self.reservations.today().upcoming()


class ReservationQuerySet(models.QuerySet):
    def today(self):
        return self.filter(date=timezone.now().date())

    def on_table(self, table: Table):
        return self.filter(table=table)

    def upcoming(self):
        now = timezone.now()
        return self.filter(from_time__gt=now.time())


class ReservationManager(models.Manager):
    _queryset_class = ReservationQuerySet

    def today(self):
        return self.get_queryset().filter(date=timezone.now().date())

    def on_table(self, table: Table):
        return self.get_queryset().filter(table=table)

    def upcoming(self):
        now = timezone.now()
        return self.get_queryset().filter(from_time__gt=now.time())


class Reservation(models.Model):
    date = models.DateField(_('Reservation Date'), validators=[present_or_future_date],)
    from_time = models.TimeField(_('From time'), validators=[present_or_future_time])
    to_time = models.TimeField(_('To time'), validators=[present_or_future_time])
    table = models.ForeignKey(Table, related_name='reservations', on_delete=models.CASCADE, verbose_name=_('Table'))
    persons = models.PositiveSmallIntegerField(null=True, blank=True)
    objects = ReservationManager()

    class Meta:
        unique_together = ('date', 'from_time', 'to_time')
        ordering = ['date', 'from_time']
        permissions = (
            ('can_manage_reservation', 'Can manage reservation'),
        )

    @property
    def is_in_future(self):
        now = timezone.now()
        return self.date >= now.date() and self.from_time >= now.time()

    def __str__(self):
        return f'{self.date}: {self.from_time}-{self.to_time}'
