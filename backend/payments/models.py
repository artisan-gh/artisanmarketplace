import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


# ─── Base Model (inline since common may not exist) ──────
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ─── Payment Model ─────────────────────────────────────────
class Payment(TimeStampedModel):
    """
    Payment record for a booking, integrated with Paystack/Stripe.
    """

    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        INITIATED = 'INITIATED', 'Initiated'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'
        PARTIALLY_REFUNDED = 'PARTIALLY_REFUNDED', 'Partially Refunded'

    class PaymentMethod(models.TextChoices):
        CARD = 'CARD', 'Card'
        BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'
        MOBILE_MONEY = 'MOBILE_MONEY', 'Mobile Money'
        WALLET = 'WALLET', 'Wallet'

    # ─── Relations ────────────────────────────────────────────
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    # ⚠️ BOOKING_REMOVED: The bookings app was deleted.
    # If you need to link payments to bookings later, create a new Booking model.
    # For now, this field is commented out.
    #
    # booking = models.ForeignKey(
    #     'bookings.Booking',
    #     on_delete=models.CASCADE,
    #     related_name='payments',
    #     null=True,
    #     blank=True
    # )

    # ─── Financial ────────────────────────────────────────────
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='GHS')
    fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Processing fee charged by the payment gateway"
    )
    net_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        help_text="Amount after fees (auto-calculated)"
    )

    # ─── Gateway References ───────────────────────────────────
    transaction_reference = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique reference for this transaction (generated)"
    )
    gateway_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Reference from the payment gateway (Paystack/Stripe)"
    )
    gateway_response = models.JSONField(
        default=dict,
        blank=True,
        help_text="Full response from the payment gateway"
    )

    # ─── Status ──────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        blank=True
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    # ─── Refund ──────────────────────────────────────────────
    refunded_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    refund_reference = models.CharField(max_length=100, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    refund_reason = models.TextField(blank=True)

    # ─── Metadata ─────────────────────────────────────────────
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_reference']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['paid_at']),
        ]
        verbose_name_plural = "Payments"

    def save(self, *args, **kwargs):
        if not self.transaction_reference:
            self.transaction_reference = self.generate_reference()
        self.net_amount = self.amount - self.fee
        self.full_clean()
        super().save(*args, **kwargs)

    def generate_reference(self):
        return f"PAY-{uuid.uuid4().hex[:12].upper()}"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Amount must be greater than zero.")
        if self.fee < 0:
            raise ValidationError("Fee cannot be negative.")
        if self.refunded_amount > self.amount:
            raise ValidationError("Refunded amount cannot exceed the original amount.")

    # ─── Properties ──────────────────────────────────────────
    @property
    def is_successful(self):
        return self.status == self.PaymentStatus.SUCCESS

    @property
    def is_refunded(self):
        return self.status in [self.PaymentStatus.REFUNDED, self.PaymentStatus.PARTIALLY_REFUNDED]

    @property
    def refund_balance(self):
        return self.amount - self.refunded_amount

    # ─── Status transitions ──────────────────────────────────
    def mark_successful(self, gateway_ref=None, gateway_response=None):
        if self.status not in [self.PaymentStatus.PENDING, self.PaymentStatus.INITIATED]:
            raise ValueError("Payment must be pending or initiated to mark as successful.")
        self.status = self.PaymentStatus.SUCCESS
        self.paid_at = timezone.now()
        if gateway_ref:
            self.gateway_reference = gateway_ref
        if gateway_response:
            self.gateway_response = gateway_response
        self.save()

    def mark_failed(self, gateway_response=None):
        if self.status == self.PaymentStatus.SUCCESS:
            raise ValueError("Cannot mark a successful payment as failed.")
        self.status = self.PaymentStatus.FAILED
        if gateway_response:
            self.gateway_response = gateway_response
        self.save()

    def initiate(self, gateway_ref=None):
        if self.status != self.PaymentStatus.PENDING:
            raise ValueError("Only pending payments can be initiated.")
        self.status = self.PaymentStatus.INITIATED
        if gateway_ref:
            self.gateway_reference = gateway_ref
        self.save()

    def refund(self, amount=None, reason=""):
        if not self.is_successful:
            raise ValueError("Only successful payments can be refunded.")
        refund_amount = amount or self.amount
        if refund_amount <= 0:
            raise ValueError("Refund amount must be positive.")
        if refund_amount > self.refund_balance:
            raise ValueError(f"Refund amount exceeds remaining balance of {self.refund_balance}.")
        self.refunded_amount += refund_amount
        self.refund_reason = reason
        self.refunded_at = timezone.now()
        if self.refunded_amount == self.amount:
            self.status = self.PaymentStatus.REFUNDED
        else:
            self.status = self.PaymentStatus.PARTIALLY_REFUNDED
        self.refund_reference = f"REF-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        self.save()
        return refund_amount

    def __str__(self):
        return f"{self.transaction_reference} - {self.amount} {self.currency}"
