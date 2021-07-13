from django.db.models import F
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver, Signal

from ecommerce import get_tomorrow_date
from ecommerce.models import Order, OrderStatusChange, IndexContent, OrderLine, Settings

order_line_deleted = Signal()


@receiver(pre_save, sender=Order)
def order_pre_creation_signal(sender, instance: Order, raw, **kwargs):
    if not instance.pk:
        instance.number = Order.generate_number()

    if instance.status == 'CO':
        instance.delivery_date = get_tomorrow_date()


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


@receiver(pre_save, sender=OrderLine)
def order_line_pre_creation(sender, instance: OrderLine, **kwargs):
    if not instance.pk and not kwargs.get('raw', False):
        instance.total_price = instance.total


@receiver(post_save, sender=OrderLine)
def order_line_created(sender, instance: OrderLine, created, raw, **kwargs):
    if created:
        instance.product.stock = F('stock') - instance.quantity


@receiver(order_line_deleted)
def order_line_deleted_handler(sender, instance: OrderLine, **kwargs):
    instance.product.stock = F('stock') + instance.quantity


def get_request():
    import inspect
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            break
    else:
        request = None
    return request


def prepare_index_content():
    if not IndexContent.objects.filter(pk=1).exists():
        IndexContent.objects.create()

    if not Settings.objects.filter(pk=1).exists():
        Settings.objects.create()


try:
    prepare_index_content()
except Exception:
    pass
