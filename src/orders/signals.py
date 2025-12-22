from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order

@receiver(pre_save, sender=Order)
def order_status_change_handler(sender, instance, **kwargs):
    if not instance.pk:
        return
        
    try:
        old_order = Order.objects.get(pk=instance.pk)
    except Order.DoesNotExist:
        return

    # Check if status changed to 'cancelled'
    if instance.status == 'cancelled' and old_order.status != 'cancelled':
        # Refund bonuses
        if instance.user and instance.bonuses_used > 0:
            instance.user.loyalty_points += instance.bonuses_used
            instance.user.save()
            # Optionally note this somewhere, but simplifying for now
