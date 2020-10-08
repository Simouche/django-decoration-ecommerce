from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Profile
from ecommerce.models import Cart


@receiver(post_save, sender=Profile)
def user_created_signal(sender, instance, created, raw, **kwargs):
    if created and not raw:
        Cart.objects.create(profile=instance)

