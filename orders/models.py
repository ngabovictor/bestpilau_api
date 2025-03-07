from django.db import models
from django.dispatch import receiver

from notifications.sms import send_sms_task
from utils.functions import generate_code
from utils.models import BaseModel
from utils.fields import LOCATION_DEFINITION_SCHEMA, JSONSchemaField
from auditlog.registry import auditlog
from django.db.models.signals import post_save
from notifications.push import send_push_notification

FEES_BREAKDOWN_SCHEMA = {
    "type": "object",
    "properties": {
        "subtotal": {"type": "number"},
        "discount": {"type": "number"},
        "adjustments": {"type": "number"},
        "delivery_fee": {"type": "number"},
        "service_fee": {"type": "number"},
        "total": {"type": "number"}
    },
    "required": ["subtotal", "total", "adjustments", "delivery_fee", "service_fee", "discount"]
}


class Order(BaseModel):
    reference_code = models.CharField(max_length=8, unique=True, default=generate_code)
    outlet = models.ForeignKey('outlets.Outlet', related_name='orders', on_delete=models.PROTECT)
    customer = models.ForeignKey('authentication.User', related_name='orders', on_delete=models.PROTECT)
    delivery_address = JSONSchemaField(schema=LOCATION_DEFINITION_SCHEMA, null=True)
    assigned_rider = models.ForeignKey('authentication.User', related_name='assigned_orders', on_delete=models.SET_NULL, null=True, blank=True)
    products = models.JSONField(default=list)
    total_amount = models.DecimalField(decimal_places=2, max_digits=20)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'PENDING'),
            ('CONFIRMED', 'CONFIRMED'), 
            ('PREPARING', 'PREPARING'),
            ('READY', 'READY'),
            ('DELIVERING', 'DELIVERING'),
            ('COMPLETED', 'COMPLETED'),
            ('CANCELLED', 'CANCELLED')
        ],
        default='PENDING'
    )
    notes = models.TextField(null=True, blank=True)
    cancelled_reason = models.TextField(null=True, blank=True)
    estimated_completion_time = models.DateTimeField(null=True, blank=True)
    coupon = models.ForeignKey('coupons.Coupon', related_name='orders', on_delete=models.SET_NULL, null=True, blank=True)

    fees_breakdown = JSONSchemaField(schema=FEES_BREAKDOWN_SCHEMA)

    def __str__(self):
        return f"Order {self.reference_code}"

@receiver(post_save, sender=Order)
def post_save_order(sender, instance=None, created=False, **kwargs):
    if instance:
        tracker = OrderStatusTracker.objects.filter(order=instance, status=instance.status).first()
        if not tracker:
            tracker = OrderStatusTracker(
                order=instance,
                status=instance.status
            )
            tracker.save()
            
            # Send notification to the driver if order is assigned and ready to be delivered
            if instance.status == 'READY' and instance.assigned_rider:
                send_sms_task(message=f'Wahawe komande nshya! Nomero ya komande: #{instance.reference_code}. Numero y\'umukiriya: {instance.customer.username}, aderesi: {instance.delivery_address.get("address")}', phone_numbers=[instance.assigned_rider.username])
                send_push_notification(subject=f'Komande nshya!', message=f'Wahawe komande nshya! Nomero ya komande: #{instance.reference_code}. Numero y\'umukiriya: {instance.customer.username}, aderesi: {instance.delivery_address.get("address")}', recipients=[instance.assigned_rider.username])
                
            # Send notification to customer if order is on the way
            if instance.status == 'DELIVERING' and instance.assigned_rider:
                send_sms_task(message=f'Your order from Best Pilau is on its way! {instance.assigned_rider.first_name} is delivering it. You can reach out at {instance.assigned_rider.username} if needed.', phone_numbers=[instance.customer.username])
                send_push_notification(subject=f'Order on the way!', message=f'Your order from Best Pilau is on its way! {instance.assigned_rider.first_name} is delivering it. You can reach out at {instance.assigned_rider.username} if needed.', recipients=[instance.customer.username])
                
            if instance.status == 'PREPARING':
                send_push_notification(subject=f'Order is being prepared!', message=f'Your order from Best Pilau is being prepared. It will be ready for delivery soon.', recipients=[instance.customer.username])



auditlog.register(Order)


class OrderStatusTracker(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=[
            ('PENDING', 'PENDING'),
            ('CONFIRMED', 'CONFIRMED'), 
            ('PREPARING', 'PREPARING'),
            ('READY', 'READY'),
            ('DELIVERING', 'DELIVERING'),
            ('COMPLETED', 'COMPLETED'),
            ('CANCELLED', 'CANCELLED')
        ],
    )

    class Meta:
        ordering = ("created_at",)

auditlog.register(OrderStatusTracker)