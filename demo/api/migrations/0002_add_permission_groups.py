from django.db import migrations


def create_groups(apps, schema_editor):
    del schema_editor
    group_model = apps.get_model('auth', 'Group')

    group_model.objects.get_or_create(name='account_manager')
    group_model.objects.get_or_create(name='customer_support')


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(
            create_groups, reverse_code=migrations.RunPython.noop),
    ]
