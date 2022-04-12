from django.db import migrations


def add_all_permissions(apps=None, schema_editor=None):
    from django.contrib.auth.management import create_permissions

    if apps is None:
        from django.apps import apps

    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None


def add_admin_permission(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    admin, _ = Role.objects.get_or_create(name='admin')

    Permission = apps.get_model('auth', 'Permission')

    Table = apps.get_model('reservations', 'Table')
    ContentType = apps.get_model("contenttypes", "ContentType")
    content_type = ContentType.objects.get_for_model(Table)

    perm = Permission.objects.get(codename='can_manage_tables', content_type=content_type)

    admin.permissions.add(perm)


def remove_admin_permission(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    Permission = apps.get_model('auth', 'Permission')

    can_manage_perm = Permission.objects.get(codename='can_manage_tables')
    Role.permissions.remove(can_manage_perm)


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_all_permissions, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(add_admin_permission, remove_admin_permission, atomic=True),
    ]
