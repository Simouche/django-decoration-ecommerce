from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User, Profile


@receiver(post_save, sender=User)
def user_created_signal(sender, instance, created, raw, **kwargs):
    if created:
        Profile.objects.create(user=instance)
