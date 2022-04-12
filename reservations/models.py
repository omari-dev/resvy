from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Table(models.Model):
    number = models.PositiveIntegerField(_('Table Number'), unique=True, blank=False, null=False)
    number_of_seats = models.PositiveIntegerField(_('Number of seats'),
                                                  unique=False,
                                                  blank=False,
                                                  null=True,
                                                  validators=(MinValueValidator(1), MaxValueValidator(12)),)

    class Meta:
        permissions = (
            ('can_manage_tables', 'Can manage Table'),
        )

    def __str__(self) -> str:
        return f'Table number: {self.number}, Number of seats: {self.number_of_seats}'

    @property
    def can_be_deleted(self) -> bool:
        return True
