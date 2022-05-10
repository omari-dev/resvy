from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group
from django.core.cache import cache
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    A custom user manager to deal with employee number as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """

    def create_user(self, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(password, **extra_fields)

    def _create_user(self, password, **extra_fields):
        """
        Creates and saves a User with the given employee number and password.
        """
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, employee_no, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(employee_no, password, **extra_fields)


class User(AbstractUser):
    USERNAME_FIELD = 'employee_no'
    REQUIRED_FIELDS = []

    is_staff = None
    email = None
    username = None

    employee_no = models.CharField(
        _('Employee Number'),
        max_length=4,
        validators=(MinLengthValidator(4),),
        unique=True,
        blank=False,
        null=False,
    )
    objects = UserManager()

    class Meta:
        db_table = 'auth_user'
        permissions = (
            ('can_add_employee', 'Can add employee'),
        )

    def __str__(self):
        return f'{self.employee_no}: {self.first_name} {self.last_name}'

    def get_roles(self):
        roles = cache.get(self.employee_no)
        if not roles:
            roles = list(self.groups.all().values_list('name', flat=True))
            cache.set(self.employee_no, roles)
        return roles

    @cached_property
    def is_admin(self):
        return self.groups.filter(name=Role.ADMIN).exists()

    @cached_property
    def is_employee(self):
        return self.groups.filter(name=Role.EMPLOYEE).exists()


class Role(Group):
    ADMIN = 'admin'
    EMPLOYEE = 'employee'

    class Meta:
        proxy = True
