from django.db import migrations
from django.contrib.auth.hashers import make_password


EMPLOYEE_NO = '0001'


def create_admin_group(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    admin, _ = Role.objects.get_or_create(name='admin')

    Permission = apps.get_model('auth', 'Permission')

    User = apps.get_model('users', 'User')
    ContentType = apps.get_model("contenttypes", "ContentType")
    content_type = ContentType.objects.get_for_model(User)

    perm = Permission.objects.get(codename='can_add_employee', content_type=content_type)

    admin.permissions.add(perm)


def add_all_permissions(apps=None, schema_editor=None):
    from django.contrib.auth.management import create_permissions

    if apps is None:
        from django.apps import apps

    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None


def remove_admin_group(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    Permission = apps.get_model('auth', 'Permission')

    Permission.objects.filter(codename='can_add_employee').delete()
    Role.objects.filter(name='admin').delete()


def init_admin_users(apps, schema_editor):
    User = apps.get_model('users', 'User')
    user = User(first_name='admin', last_name='al admin', employee_no=EMPLOYEE_NO, )

    user.password = make_password('A1230838a')
    user.save()

    Role = apps.get_model('users', 'Role')
    user.groups.add(Role.objects.get(name='admin'))


def revert_init_admin_user(apps, schema_editor):
    User = apps.get_model('users', 'User')
    User.objects.filter(employee_no=EMPLOYEE_NO).delete()


def init_employee_role(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    employee, _ = Role.objects.get_or_create(name='employee')


def revert_init_employee_role(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    Role.objects.filter(name='employee').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_all_permissions, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(create_admin_group, remove_admin_group, atomic=True),
        migrations.RunPython(init_admin_users, revert_init_admin_user, atomic=True),
        migrations.RunPython(init_employee_role, revert_init_employee_role, atomic=True)
    ]
