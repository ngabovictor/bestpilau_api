from django.db import models
from django.dispatch import receiver

from utils.functions import generate_code
from utils.models import BaseModel
from utils.fields import LOCATION_DEFINITION_SCHEMA, JSONSchemaField
from auditlog.registry import auditlog
from django.db.models.signals import post_save

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