import factory

from django.contrib.auth.hashers import make_password

from factory.django import DjangoModelFactory as Factory
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User


class UserFactory(Factory):
    employee_no = factory.Faker('pystr_format', string_format="####")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        user = User(**kwargs)
        user.password = make_password('password')
        user.save()
        return user


class UserWithTokenFactory(UserFactory):
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = super()._create(model_class, *args, **kwargs)
        serializer = TokenObtainPairSerializer(data={'employee_no': user.employee_no, 'password': 'password'})
        serializer.is_valid(raise_exception=True)
        setattr(user, 'token', serializer.validated_data['access'])
        setattr(user, 'credentials', {"HTTP_AUTHORIZATION": f"Bearer {user.token}"})
        return user
