from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User, Role


class CreateEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'employee_no',
            'first_name',
            'last_name',
            'password',
        )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    @classmethod
    def validate_password(cls, password):
        validate_password(password)
        return password

    @classmethod
    def validate_employee_no(cls, employee_no):
        if not employee_no.isdigit():
            raise serializers.ValidationError(_('Only digits are allowed'))
        return employee_no

    @classmethod
    @transaction.atomic
    def create(cls, validated_data):
        user: User = User.objects.create_user(**validated_data)
        employee_group = Role.objects.get(name=Role.EMPLOYEE)
        user.groups.add(employee_group)
        return user


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name')


class UserInfoSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_full_name')
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'name',
            'employee_no',
            'role'
        )

    @classmethod
    def get_role(cls, user: User):
        return RoleSerializer(instance=user.groups.last()).data


class UserInfoTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        for k, v in UserInfoSerializer(user).data.items():
            token[k] = v

        return token
