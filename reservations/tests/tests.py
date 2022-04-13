from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from users.models import Role
from users.tests.factories import UserWithTokenFactory
from .factories import TableFactory
from ..models import Table


class TableTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = UserWithTokenFactory()
        cls.admin_user.groups.add(Role.objects.get(name=Role.ADMIN))

    def setUp(self) -> None:
        self.client.credentials(**self.admin_user.credentials)

    def test_admin_retrieve_tables_success(self):
        TableFactory.create_batch(size=10)
        response = self.client.get(reverse('tables-api-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        table = data['results'][0]
        self.assertIn('number', table.keys())
        self.assertIn('number_of_seats', table.keys())

    def test_employee_retrieve_tables_will_be_unauthorized(self):
        employee = UserWithTokenFactory()
        employee.groups.add(Role.objects.get(name=Role.EMPLOYEE))
        self.client.credentials(**employee.credentials)
        response = self.client.get(reverse('tables-api-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_retrieve_tables_will_be_unauthorized(self):
        self.client.credentials(**{})
        response = self.client.get(reverse('tables-api-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_add_new_table_success(self):
        data = {'number': 1, 'number_of_seats': 5}
        response = self.client.post(reverse('tables-api-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_add_table_with_more_than_maximum_number_of_seat_will_fail(self):
        data = {'number': 1, 'number_of_seats': 13}
        response = self.client.post(reverse('tables-api-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Ensure this value is less than or equal to', response.json()['number_of_seats'][0])

    def test_admin_add_table_with_less_than_minimum_number_of_seat_will_fail(self):
        data = {'number': 1, 'number_of_seats': 0}
        response = self.client.post(reverse('tables-api-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Ensure this value is greater than or equal to', response.json()['number_of_seats'][0])

    def test_admin_delete_available_table_will_success(self):
        table = TableFactory()
        url = reverse('tables-api-detail', kwargs={'pk': table.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Table.objects.filter(pk=table.pk).exists())

    # TODO: cover tables can not be deleted
