import email
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.dispatch import receiver
from django.db.models.signals import post_save
from guardian.shortcuts import assign_perm
import django.utils.timezone
from typing import TYPE_CHECKING


def now():
    return django.utils.timezone.now().date()


class DeletedData(models.Model):
    model_type = models.CharField(max_length=200)
    model_id = models.IntegerField()
    data = models.TextField()


class Package(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    promo = models.TextField()
    price = models.FloatField()
    rating = models.CharField(max_length=50)
    tour_length = models.IntegerField()
    start = models.DateField(default=now)

    def __str__(self):
        return self.name


class Booking(models.Model):
    package = models.ForeignKey(Package, null=True, on_delete=models.SET_NULL)
    start = models.DateField()
    name = models.CharField(max_length=200)
    email_address = models.CharField(max_length=200)

    def __str__(self):
        return '{} for {} on {}'.format(self.name, self.package.name, self.start)

    def delete(self, *args, **kwargs):
        booking_data = serializers.serialize('json', [self])
        DeletedData.objects.create(
            model_type='api.Booking',
            model_id=self.pk,
            data=booking_data
        )
        super().delete(*args, **kwargs)


@receiver(post_save, sender=Booking)
def assign_booking_permissions(sender, instance, created, **kwargs):
    del sender, kwargs
    user = User.objects.get(
        email=instance.email_address) if instance.email_address else None
    if created and user:
        assign_perm('api.change_booking', user, instance)
        assign_perm('api.view_booking', user, instance)
        assign_perm('api.delete_booking', user, instance)


class PackagePermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    is_owner = models.BooleanField(blank=False, default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'package'], name='unique_owner'),
        ]

    def __str__(self):
        if self.is_owner:
            fmt = '{} ({}) can write to {} ({})'
        else:
            fmt = '{} ({}) cannot write to {}'
        return fmt.format(self.user.username, self.user.id, self.package.name, self.package.id)

    @classmethod  # type: ignore
    def can_write(cls, user: User, package: 'Package') -> bool:
        try:
            permission = cls.objects.get(user=user, package=package)
            return permission.is_owner
        except ObjectDoesNotExist:
            return False

    @classmethod  # type: ignore
    def set_can_write(cls, user: User, package: 'Package') -> None:
        obj, created = cls.objects.get_or_create(
            user=user, package=package, defaults={'is_owner': True})
        if not created:
            obj.is_owner = True
            obj.save()


class ActivityLog(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=300)


def restore_booking(booking_id: int) -> None:
    """Restore a deleted booking from DeletedData"""
    try:
        deleted_data = DeletedData.objects.get(
            model_type='api.Booking',
            model_id=booking_id
        )

        booking_data = serializers.deserialize('json', deleted_data.data)
        booking_obj = next(booking_data)

        booking_obj.save()

        deleted_data.delete()

    except DeletedData.DoesNotExist:
        raise ValueError(f"No deleted booking found with ID {booking_id}")
