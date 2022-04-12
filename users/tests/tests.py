from faker import Faker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from users.models import User, Role
from users.tests.factories import UserWithTokenFactory, UserFactory


class UserTestCases(APITestCase):
    @classmethod
    def setUpTestData(cls):
        fake = Faker()
        cls.data = {
            'employee_no': fake.pystr_format(string_format="####"),
            'first_name': "Omar",
            'last_name': "alomri",
            'password': 'A23BA123',
        }
        cls.login_url = reverse('login')
        cls.register_user_url = reverse('user-register')

        cls.admin_user = UserWithTokenFactory()
        cls.admin_user.groups.add(Role.objects.get(name=Role.ADMIN))

    def setUp(self) -> None:
        self.client.credentials(**self.admin_user.credentials)

    def test_create_employee_success(self):
        resp = self.client.post(self.register_user_url, data=self.data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(employee_no=self.data['employee_no']).exists())
        employee_user = User.objects.get(employee_no=self.data['employee_no'])
        self.assertTrue(employee_user.groups.filter(name=Role.EMPLOYEE).exists())

    def test_create_employee_with_existing_employee_number_will_fail(self):
        employee = UserFactory()
        duplicate_data = self.data.copy()
        duplicate_data['employee_no'] = employee.employee_no
        resp = self.client.post(self.register_user_url, data=duplicate_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.json()['employee_no'], ['user with this Employee Number already exists.'])

    def test_create_employee_with_missing_employee_number_will_fail(self):
        broken_data = self.data.copy()
        _ = broken_data.pop('employee_no')
        resp = self.client.post(self.register_user_url, data=broken_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.json()['employee_no'], ['This field is required.'])

    def test_create_employee_with_less_than_accepted_employee_number_will_fail(self):
        broken_data = self.data.copy()
        broken_data['employee_no'] = '12'
        resp = self.client.post(self.register_user_url, data=broken_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.json()['employee_no'], ['Ensure this field has at least 4 characters.'])

    def test_create_employee_with_more_than_valid_employee_number_will_fail(self):
        broken_data = self.data.copy()
        broken_data['employee_no'] = '12345'
        resp = self.client.post(self.register_user_url, data=broken_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.json()['employee_no'], ['Ensure this field has no more than 4 characters.'])

    def test_create_employee_with_invalid_employee_number_will_fail(self):
        invalid_data = self.data.copy()
        invalid_data['employee_no'] = '!AS2'
        resp = self.client.post(self.register_user_url, data=invalid_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.json()['employee_no'], ['Only digits are allowed'])

    def test_create_user_with_missing_first_name_will_fail(self):
        broken_data = self.data.copy()
        _ = broken_data.pop('first_name')
        resp = self.client.post(self.register_user_url, data=broken_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.json()['first_name'], ['This field is required.'])

    def test_admin_logged_success(self):
        resp = self.client.post(self.login_url,
                                data={'employee_no': self.admin_user.employee_no, 'password': 'password'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.json())

    def test_verify_user_token_success(self):
        user = UserWithTokenFactory()
        resp = self.client.post(reverse('verify-token'), data={'token': user.token})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_verify_user_invalid_token(self):
        user = UserWithTokenFactory()
        resp = self.client.post(reverse('verify-token'), data={'token': user.token + 'ld123'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_registered_user_success(self):
        self.client.credentials(**self.admin_user.credentials)
        self.data['username'] = 'new_user'
        resp = self.client.post(reverse('user-register'), data=self.data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        self.client.credentials(**{})
        data = {'employee_no': self.data['employee_no'], 'password': self.data['password']}
        resp = self.client.post(self.login_url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # TODO: inspect response payload
