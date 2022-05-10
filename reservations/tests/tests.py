import datetime

from unittest import mock

from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from users.models import Role
from users.tests.factories import UserWithTokenFactory
from .factories import TableFactory
from ..models import Table, Reservation


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

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2025, 1, 1, 17, 00))
    def test_admin_delete_table_which_has_upcoming_reservation_will_fail(self, _):
        table = TableFactory()
        Reservation.objects.create(
            date=datetime.date(2025, 1, 1),
            from_time=datetime.time(19, 00),
            to_time=datetime.time(19, 30),
            table=table,
            persons=3
        )
        url = reverse('tables-api-detail', kwargs={'pk': table.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Table.objects.filter(pk=table.pk).exists())


class AvailabilityTestCases(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = UserWithTokenFactory()
        cls.admin_user.groups.add(Role.objects.get(name=Role.ADMIN))

    def setUp(self) -> None:
        self.client.credentials(**self.admin_user.credentials)

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 14, 00))
    def test_first_scenario_success(self, _):
        Table.objects.create(number=1, number_of_seats=2)
        response = self.client.get(reverse('tables-api-availability') + '?number_of_persons=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_result = ['02:00 PM', '11:59 PM']
        time_slot = response.json()[0]['availability'][0]
        returned_time_slots = [time_slot[0], time_slot[1]]
        self.assertEqual(expected_result, returned_time_slots)

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 13, 00))
    def test_second_scenario_success(self, _):
        table = Table.objects.create(number=1, number_of_seats=4)

        Reservation.objects.create(
            date=datetime.date(2030, 1, 1),
            from_time=datetime.time(16, 00),
            to_time=datetime.time(16, 30),
            table=table,
            persons=3
        )
        Reservation.objects.create(
            date=datetime.date(2030, 1, 1),
            from_time=datetime.time(17, 30),
            to_time=datetime.time(17, 45),
            table=table,
            persons=5
        )
        response = self.client.get(reverse('tables-api-availability') + '?number_of_persons=3')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        time_slots = response.json()[0]['availability']
        self.assertIn(["01:00 PM", "04:00 PM"], time_slots)
        self.assertIn(["04:30 PM", "05:30 PM"], time_slots)
        self.assertIn(["05:45 PM", "11:59 PM"], time_slots)

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 5, 00))
    def test_check_availability_before_working_hours(self, _):
        Table.objects.create(number=1, number_of_seats=3)
        response = self.client.get(reverse('tables-api-availability') + '?number_of_persons=3')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_result = ['12:00 PM', '11:59 PM']
        time_slot = response.json()[0]['availability'][0]
        returned_time_slots = [time_slot[0], time_slot[1]]
        self.assertEqual(expected_result, returned_time_slots)

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 5, 00))
    def test_return_empty_response_when_working_hours(self, _):
        table = Table.objects.create(number=1, number_of_seats=3)
        Reservation.objects.create(
            date=datetime.date(2030, 1, 1),
            from_time=datetime.time(12, 00),
            to_time=datetime.time(23, 59),
            table=table,
            persons=3
        )
        response = self.client.get(reverse('tables-api-availability') + '?number_of_persons=3')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        time_slot = response.json()[0]['availability']
        self.assertFalse(time_slot)

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 5, 00))
    def test_when_admin_pass_invalid_number_of_person_will_fail(self, _):
        Table.objects.create(number=1, number_of_seats=2)
        response = self.client.get(reverse('tables-api-availability') + '?number_of_persons=ABC')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # todo check for the response payload

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 5, 00))
    def test_admin_check_table_for_exceed_number_of_person_will_fail(self, _):
        Table.objects.create(number=1, number_of_seats=2)
        response = self.client.get(reverse('tables-api-availability') + '?number_of_persons=500')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # todo check for the response payload


class ReservationTestCases(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = UserWithTokenFactory()
        cls.admin_user.groups.add(Role.objects.get(name=Role.ADMIN))

        cls.employee = UserWithTokenFactory()
        cls.employee.groups.add(Role.objects.get(name=Role.EMPLOYEE))

    def setUp(self) -> None:
        self.client.credentials(**self.admin_user.credentials)

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 17, 00))
    def test_admin_create_a_reservation_for_with_no_other_reservation_will_success(self, _):
        """ the most easy test will handle restaurant with one table with no other reservation """
        table = Table.objects.create(number=1, number_of_seats=2)
        data = {'from_time': '17:30', "to_time": "18:00", 'persons': 2, 'table': table.id}
        response = self.client.post(reverse('reservation-api-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Reservation.objects.filter(table=table, from_time=data['from_time'], to_time=data['to_time']).exists()
        )

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 17, 00))
    def test_employee_create_a_reservation_for_with_no_other_reservation_will_success(self, _):
        self.client.credentials(**self.employee.credentials)
        table = Table.objects.create(number=1, number_of_seats=3)
        data = {'from_time': '17:30', "to_time": "18:00", 'persons': 3, 'table': table.id}
        response = self.client.post(reverse('reservation-api-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Reservation.objects.filter(table=table, from_time=data['from_time'], to_time=data['to_time']).exists()
        )

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 17, 00))
    def test_admin_reserve_table_for_only_one_person_with_table_for_two_success(self, _):
        table = Table.objects.create(number=1, number_of_seats=2)
        data = {'from_time': '17:30', "to_time": "18:00", 'persons': 1, 'table': table.id}
        response = self.client.post(reverse('reservation-api-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Reservation.objects.filter(table=table, from_time=data['from_time'], to_time=data['to_time']).exists()
        )

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 17, 00))
    def test_admin_reserve_time_slot_before_restaurant_opens_will_fail(self, _):
        table = Table.objects.create(number=1, number_of_seats=1)
        data = {'from_time': '11:30', "to_time": "15:00", 'persons': 1, 'table': table.id}
        response = self.client.post(reverse('reservation-api-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            Reservation.objects.filter(table=table, from_time=data['from_time'], to_time=data['to_time']).exists()
        )

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 18, 00))
    def test_admin_reserve_past_time_slot_will_fail(self, _):
        table = Table.objects.create(number=1, number_of_seats=1)
        data = {'from_time': '17:30', "to_time": "18:30", 'persons': 1, 'table': table.id}
        response = self.client.post(reverse('reservation-api-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            Reservation.objects.filter(table=table, from_time=data['from_time'], to_time=data['to_time']).exists()
        )

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 18, 00))
    def test_admin_reserve_invalid_date_duration_will_fail(self, _):
        table = Table.objects.create(number=1, number_of_seats=4)
        data = {'from_time': '17:30', "to_time": "16:30", 'persons': 4, 'table': table.id}
        response = self.client.post(reverse('reservation-api-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            Reservation.objects.filter(table=table, from_time=data['from_time'], to_time=data['to_time']).exists()
        )

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 18, 00))
    def test_admin_reserve_malformed_date_duration_will_fail(self, _):
        table = Table.objects.create(number=1, number_of_seats=3)
        data = {'from_time': '1730', "to_time": "18:30", 'persons': 2, 'table': table.id}
        response = self.client.post(reverse('reservation-api-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Time has wrong format.', response.json()['from_time'][0])


class ListReservationTestCases(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = UserWithTokenFactory()
        cls.admin_user.groups.add(Role.objects.get(name=Role.ADMIN))

        cls.employee = UserWithTokenFactory()
        cls.employee.groups.add(Role.objects.get(name=Role.EMPLOYEE))

        # Todo: use factory instead
        table = Table.objects.create(number=1, number_of_seats=2)
        cls.reservation1 = Reservation.objects.create(
            date=datetime.date(2030, 1, 1),
            from_time=datetime.time(16, 00),
            to_time=datetime.time(16, 30),
            table=table,
            persons=3
        )
        cls.reservation2 = Reservation.objects.create(
            date=datetime.date(2030, 1, 1),
            from_time=datetime.time(17, 00),
            to_time=datetime.time(17, 30),
            table=table,
            persons=3
        )

        cls.reservation3 = Reservation.objects.create(
            date=datetime.date(2005, 1, 1),
            from_time=datetime.time(17, 00),
            to_time=datetime.time(17, 30),
            table=table,
            persons=3
        )
        cls.list_reservation_url = reverse('reservation-api-list')

    def setUp(self) -> None:
        self.client.credentials(**self.admin_user.credentials)

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 15, 00))
    def test_admin_list_today_reservation_success(self, _):
        response = self.client.get(self.list_reservation_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 2)
        returned_reservation_ids = [res['id'] for res in data['results']]
        self.assertIn(self.reservation1.id, returned_reservation_ids)
        self.assertIn(self.reservation2.id, returned_reservation_ids)

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 15, 00))
    def test_employee_list_today_reservation_success(self, _):
        self.client.credentials(**self.employee.credentials)
        response = self.client.get(self.list_reservation_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 2)
        returned_reservation_ids = [res['id'] for res in data['results']]
        self.assertIn(self.reservation1.id, returned_reservation_ids)
        self.assertIn(self.reservation2.id, returned_reservation_ids)

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2035, 1, 1, 18, 00))
    def test_past_reservation_will_not_be_returned_by_default(self, _):
        self.client.credentials(**self.employee.credentials)
        response = self.client.get(self.list_reservation_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 0)

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2035, 1, 1, 18, 00))
    def test_admin_list_all_reservation_success(self, _):
        self.client.credentials(**self.admin_user.credentials)
        response = self.client.get(self.list_reservation_url + '?all=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 3)

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 18, 00))
    def test_employee_tries_to_list_all_reservation_will_be_ignored(self, _):
        self.client.credentials(**self.employee.credentials)
        response = self.client.get(self.list_reservation_url + '?all=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 2)


class DeleteReservationTestCases(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = UserWithTokenFactory()
        cls.admin_user.groups.add(Role.objects.get(name=Role.ADMIN))

        cls.employee = UserWithTokenFactory()
        cls.employee.groups.add(Role.objects.get(name=Role.EMPLOYEE))

    def setUp(self) -> None:
        self.client.credentials(**self.admin_user.credentials)
        # Todo: use factory instead
        table = Table.objects.create(number=1, number_of_seats=2)

        self.reservation = Reservation.objects.create(
            date=datetime.date(2030, 1, 1),
            from_time=datetime.time(16, 00),
            to_time=datetime.time(16, 30),
            table=table,
            persons=3
        )
        self.past_reservation = Reservation.objects.create(
            date=datetime.date(2006, 1, 1),
            from_time=datetime.time(17, 00),
            to_time=datetime.time(17, 30),
            table=table,
            persons=3
        )

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 13, 00))
    def test_admin_delete_today_reservation_success(self, _):
        url = reverse('reservation-api-detail', kwargs={'pk': self.reservation.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Reservation.objects.filter(pk=self.reservation.pk).exists())

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 13, 00))
    def test_employee_delete_today_reservation_success(self, _):
        self.client.credentials(**self.employee.credentials)
        url = reverse('reservation-api-detail', kwargs={'pk': self.reservation.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Reservation.objects.filter(pk=self.reservation.pk).exists())

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 13, 00))
    def test_admin_delete_past_reservation_fail(self, _):
        url = reverse('reservation-api-detail', kwargs={'pk': self.past_reservation.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Reservation.objects.filter(pk=self.past_reservation.pk).exists())


class AvailabilityAndReservationIntegrationTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = UserWithTokenFactory()
        cls.admin_user.groups.add(Role.objects.get(name=Role.ADMIN))

        cls.employee = UserWithTokenFactory()
        cls.employee.groups.add(Role.objects.get(name=Role.EMPLOYEE))

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime(2030, 1, 1, 17, 00))
    def test_availability_response_api_will_be_change_when_there_is_new_reservation(self, _):
        self.client.force_authenticate(self.admin_user)
        table = Table.objects.create(number=1, number_of_seats=4)
        response = self.client.get(reverse('tables-api-availability') + '?number_of_persons=3')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_result = ['05:00 PM', '11:59 PM']

        time_slot = response.json()[0]['availability'][0]
        returned_time_slots = [time_slot[0], time_slot[1]]
        self.assertEqual(expected_result, returned_time_slots)

        data = {'from_time': '19:30', "to_time": "20:00", 'persons': 3, 'table': table.id}
        response = self.client.post(reverse('reservation-api-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Reservation.objects.filter(table=table, from_time=data['from_time'], to_time=data['to_time']).exists()
        )

        second_response = self.client.get(reverse('tables-api-availability') + '?number_of_persons=3')
        self.assertEqual(second_response.status_code, second_response.status_code)
        self.assertNotEqual(second_response.json()[0]['availability'][0], expected_result)

        time_slot = second_response.json()[0]['availability']
        self.assertIn(['05:00 PM', '07:30 PM'], time_slot)
        self.assertIn(['08:00 PM', '11:59 PM'], time_slot)
