import factory

from factory.django import DjangoModelFactory as Factory

from ..models import Table


class TableFactory(Factory):
    number = factory.Faker('pyint',)
    number_of_seats = factory.Faker('pyint', min_value=1, max_value=12)

    class Meta:
        model = Table
