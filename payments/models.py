from django.db import models

from django.db import models
from utils.functions import generate_code
from utils.models import BaseModel
from orders.models import Order
from auditlog.registry import auditlog


class Transaction(BaseModel):
    reference_code = models.CharField(max_length=8, unique=True, default=generate_code)
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    outlet = models.ForeignKey(
        'outlets.Outlet',
        on_delete=models.SET_NULL,
        related_name='transactions',
        null=True,
        blank=True
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Transaction amount in base currency'
    )
    currency = models.CharField(
        max_length=3,
        default='RWF',
        help_text='Three-letter currency code (e.g. RWF)'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('PROCESSING', 'Processing'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
            ('REFUNDED', 'Refunded'),
            ('CANCELLED', 'Cancelled')
        ],
        default='PENDING'
    )
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('CREDIT_CARD', 'Credit Card'),
            ('DEBIT_CARD', 'Debit Card'),
            ('BANK_TRANSFER', 'Bank Transfer'),
            ('DIGITAL_WALLET', 'Digital Wallet'),
            ('MOBILE_MONEY', 'Mobile Money'),
            ('CASH', 'Cash')
        ],
        null=True,
        blank=True
    )
    payment_account_number = models.CharField(
        max_length=255,
    )
    gw_codename = models.CharField(
        max_length=255,
        help_text='Payment gateway codename'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('PAYMENT', 'Payment'),
            ('REFUND', 'Refund')
        ],
        default='PAYMENT',
        help_text='Type of transaction'
    )
    reference_id = models.CharField(
        max_length=100,
        unique=True,
        help_text='Payment gateway reference/transaction ID',
        null=True,
        blank=True
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text='Error message in case of failed transaction'
    )
    refund_status = models.CharField(
        max_length=20,
        choices=[
            ('NOT_REFUNDED', 'Not Refunded'),
            ('PARTIAL', 'Partially Refunded'),
            ('FULL', 'Fully Refunded')
        ],
        default='NOT_REFUNDED'
    )
    refunded_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Amount refunded from this transaction'
    )
    gw_request_payload = models.JSONField(
        verbose_name='Gateway Request Payload',
        null=True,
        blank=True
    )
    gw_request_response = models.JSONField(
        verbose_name='Gateway Request Response', 
        null=True,
        blank=True
    )
    gw_request_callback = models.JSONField(
        verbose_name='Gateway Request Callback',
        null=True,
        blank=True
    )

    def __str__(self):
        return f'Transaction {self.id} for Order {self.order.reference_code}'

auditlog.register(Transaction)
