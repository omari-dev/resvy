from django.core.management.base import BaseCommand, CommandError
from users.serializers import CreateEmployeeSerializer


class Command(BaseCommand):
    help = 'Command to create admin User'

    def add_arguments(self, parser):
        parser.add_argument('--employee_no', type=str,)
        parser.add_argument('--first_name', type=str)
        parser.add_argument('--last_name', type=str)
        parser.add_argument('--password', type=str)

    def handle(self, *args, **options):
        data = {
            'first_name': options['first_name'],
            'last_name': options['last_name'],
            'employee_no': options['employee_no'],
            'password': options['password']
        }

        serializer = CreateEmployeeSerializer(data=data)
        if not serializer.is_valid():
            raise CommandError(serializer.errors)

        user = serializer.save()
        self.stdout.write(self.style.SUCCESS(f'Successfully admin created with employee number: {user.employee_no}'))
