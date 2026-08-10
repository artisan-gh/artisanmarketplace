import uuid
from decimal import Decimal
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


class Invoice(TimeStampedModel):
    """
    Invoice for services rendered.
    """

    class InvoiceStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SENT = 'SENT', 'Sent'
        PAID = 'PAID', 'Paid'
        PARTIALLY_PAID = 'PARTIALLY_PAID', 'Partially Paid'
        CANCELLED = 'CANCELLED', 'Cancelled'
        OVERDUE = 'OVERDUE', 'Overdue'

    # ─── Relations ────────────────────────────────────────────
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invoices'
    )

    # ⚠️ BOOKING_REMOVED: The bookings app was deleted.
    # If you need to link invoices to bookings later, uncomment and create Booking model.
    #
    # booking = models.OneToOneField(
    #     'bookings.Booking',
    #     on_delete=models.CASCADE,
    #     related_name='invoice'
    # )

    # ─── Invoice Identification ──────────────────────────────
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Auto-generated invoice number (e.g., INV-2025-0001)"
    )

    # ─── Dates ────────────────────────────────────────────────
    issued_date = models.DateField(
        default=timezone.now,
        help_text="Date when the invoice was issued"
    )

    due_date = models.DateField(
        help_text="Date by which the invoice should be paid"
    )

    sent_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when the invoice was sent to the client"
    )

    paid_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when the invoice was fully paid"
    )

    # ─── Financial ────────────────────────────────────────────
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total before tax and discount"
    )

    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Tax rate in percentage (e.g., 7.5 for 7.5%)"
    )

    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Calculated tax amount"
    )

    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Discount amount (flat) or percentage? We'll use flat for simplicity"
    )

    discount_type = models.CharField(
        max_length=10,
        choices=[('FIXED', 'Fixed'), ('PERCENT', 'Percent')],
        default='FIXED'
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Grand total (subtotal + tax - discount)"
    )

    currency = models.CharField(
        max_length=10,
        default='GHS'
    )

    # ─── Payment References ──────────────────────────────────
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        help_text="Payment that settled this invoice"
    )

    # ─── Status ──────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT
    )

    # ─── Additional Info ──────────────────────────────────────
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True, help_text="Payment terms and conditions")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['client', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['issued_date']),
        ]
        verbose_name_plural = "Invoices"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_number()
        self.calculate_totals()
        self.full_clean()
        super().save(*args, **kwargs)

    def generate_number(self):
        year = timezone.now().strftime('%Y')
        count = Invoice.objects.filter(created_at__year=timezone.now().year).count() + 1
        return f"INV-{year}-{str(count).zfill(4)}"

    def clean(self):
        if self.due_date < self.issued_date:
            raise ValidationError("Due date must be after issued date.")
        if self.discount < 0:
            raise ValidationError("Discount cannot be negative.")
        if self.tax_rate < 0:
            raise ValidationError("Tax rate cannot be negative.")

    def calculate_totals(self):
        tax = (self.subtotal * self.tax_rate) / 100
        self.tax_amount = tax
        discount_value = 0
        if self.discount_type == 'PERCENT':
            discount_value = (self.subtotal * self.discount) / 100
        else:
            discount_value = self.discount
        # Ensure discount doesn't exceed subtotal
        discount_value = min(discount_value, self.subtotal)
        self.discount = discount_value
        self.total = self.subtotal + tax - discount_value
        return self.total

    # ─── Properties ──────────────────────────────────────────

    @property
    def is_paid(self):
        return self.status == self.InvoiceStatus.PAID

    @property
    def is_overdue(self):
        return self.status != self.InvoiceStatus.PAID and timezone.now().date() > self.due_date

    @property
    def is_draft(self):
        return self.status == self.InvoiceStatus.DRAFT

    @property
    def is_sent(self):
        return self.status == self.InvoiceStatus.SENT

    # ─── Status transitions ──────────────────────────────────

    def send(self):
        if self.status not in [self.InvoiceStatus.DRAFT, self.InvoiceStatus.SENT]:
            raise ValueError("Only draft or sent invoices can be sent.")
        self.status = self.InvoiceStatus.SENT
        self.sent_date = timezone.now().date()
        self.save()

    def mark_paid(self, payment=None):
        if self.status == self.InvoiceStatus.PAID:
            raise ValueError("Invoice already paid.")
        self.status = self.InvoiceStatus.PAID
        self.paid_date = timezone.now().date()
        if payment:
            self.payment = payment
        self.save()

    def cancel(self):
        if self.status in [self.InvoiceStatus.PAID, self.InvoiceStatus.CANCELLED]:
            raise ValueError("Cannot cancel a paid or already cancelled invoice.")
        self.status = self.InvoiceStatus.CANCELLED
        self.save()

    def check_overdue(self):
        if self.status in [self.InvoiceStatus.PAID, self.InvoiceStatus.CANCELLED, self.InvoiceStatus.OVERDUE]:
            return
        if timezone.now().date() > self.due_date:
            self.status = self.InvoiceStatus.OVERDUE
            self.save()

    def __str__(self):
        return f"{self.invoice_number} - {self.client.email}"


class InvoiceItem(TimeStampedModel):
    """
    Line item on an invoice.
    """
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items'
    )

    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Price per unit"
    )

    # ⚠️ SERVICE_REFERENCE_REMOVED: The services app may not exist.
    # If you need to link invoice items to services later, uncomment.
    #
    # service = models.ForeignKey(
    #     'services.Service',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='invoice_items'
    # )

    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(fields=['invoice']),
        ]

    @property
    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.description} ({self.quantity} x {self.unit_price})"
