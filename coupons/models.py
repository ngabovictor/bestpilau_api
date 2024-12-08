from django.db import models

from utils.models import BaseModel
from auditlog.registry import auditlog


class Coupon(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    discount_amount = models.DecimalField(decimal_places=2, max_digits=20)
    discount_type = models.CharField(
        max_length=20,
        choices=[
            ('FIXED', 'FIXED'),
            ('PERCENTAGE', 'PERCENTAGE')
        ],
        default='FIXED'
    )
    allowed_users = models.ManyToManyField('authentication.User', related_name='coupons', blank=True)
    max_uses = models.PositiveIntegerField(default=1, null=True, blank=True)
    allowed_outlets = models.ManyToManyField('outlets.Outlet', related_name='coupons', blank=True)
    all_users_allowed = models.BooleanField(default=False)
    all_outlets_allowed = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def __str__(self):
        return self.code
    


auditlog.register(Coupon)