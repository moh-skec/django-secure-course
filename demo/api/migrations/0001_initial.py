# Generated by Django 4.2.23 on 2025-07-07 00:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def now():
    return django.utils.timezone.now().date()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedData',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('model_type', models.CharField(max_length=200)),
                ('model_id', models.IntegerField()),
                ('data', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('category', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('promo', models.TextField()),
                ('price', models.FloatField()),
                ('rating', models.CharField(max_length=50)),
                ('tour_length', models.IntegerField()),
                ('start', models.DateField(default=now)),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField()),
                ('name', models.CharField(max_length=200)),
                ('email_address', models.CharField(max_length=200)),
                ('package', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.package')),
            ],
        ),
        migrations.CreateModel(
            name='PackagePermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('is_owner', models.BooleanField(blank=False, default=True)),
                ('package', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='api.package')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=300)),
                ('user', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='packagepermission',
            constraint=models.UniqueConstraint(
                fields=('user', 'package'), name='unique_owner'),
        ),
    ]
