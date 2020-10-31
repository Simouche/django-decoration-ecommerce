from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Profile, User
from ecommerce.models import Cart


@receiver(post_save, sender=Profile)
def user_profile_created_signal(sender, instance, created, raw, **kwargs):
    if created and not raw:
        Cart.objects.create(profile=instance)


@receiver(post_save, sender=User)
def user_created_signal(sender, instance, created, raw, **kwargs):
    if created and not raw:
        Profile.objects.create(user=instance)
