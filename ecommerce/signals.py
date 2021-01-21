from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from accounts.models import Profile, User
from ecommerce.models import Cart, Order, OrderStatusChange


@receiver(post_save, sender=Profile)
def user_profile_created_signal(sender, instance, created, raw, **kwargs):
    if created and not raw:
        Cart.objects.create(profile=instance)


@receiver(post_save, sender=User)
def user_created_signal(sender, instance, created, raw, **kwargs):
    if created and not raw:
        Profile.objects.create(user=instance)


@receiver(pre_save, sender=Order)
def order_pre_creation_signal(sender, instance, raw, **kwargs):
    if not instance.pk:
        instance.number = Order.generate_number()


@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, raw, **kwargs):
    request = get_request()
    if request and request.user.is_authenticated:
        if created:
            OrderStatusChange.objects.create(order=instance, previous_status='P', new_status='P', user=request.user)
        else:
            last_change = OrderStatusChange.objects.filter(order=instance).order_by('-created_at').first()
            if last_change and not last_change.new_status == instance.status:
                OrderStatusChange.objects.create(order=instance, previous_status=last_change.new_status,
                                                 new_status=instance.status, user=request.user)


def get_request():
    import inspect
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            break
    else:
        request = None
    return request
