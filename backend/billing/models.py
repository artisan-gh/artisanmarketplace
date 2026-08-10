# billing/models.py

import uuid
import secrets
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.db.models import Sum, Q, F
from django.utils import timezone

from model_utils import FieldTracker


# ============================================================
# CHOICES
# ============================================================

class InvoiceStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PENDING_MANAGER_APPROVAL = (
        "PENDING_MANAGER_APPROVAL",
        "Pending Manager Approval",
    )
    PENDING_FINANCE_APPROVAL = (
        "PENDING_FINANCE_APPROVAL",
        "Pending Finance Approval",
    )
    PENDING_DIRECTOR_APPROVAL = (
        "PENDING_DIRECTOR_APPROVAL",
        "Pending Director Approval",
    )
    APPROVED = "APPROVED", "Approved"
    SENT = "SENT", "Sent"
    VIEWED = "VIEWED", "Viewed"
    PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
    PAID = "PAID", "Paid"
    OVERDUE = "OVERDUE", "Overdue"
    CANCELLED = "CANCELLED", "Cancelled"
    VOID = "VOID", "Void"


class InvoiceType(models.TextChoices):
    STANDARD = "STANDARD", "Standard"
    PROFORMA = "PROFORMA", "Proforma"
    CREDIT_NOTE = "CREDIT_NOTE", "Credit Note"
    DEBIT_NOTE = "DEBIT_NOTE", "Debit Note"


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    INITIATED = "INITIATED", "Initiated"
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"
    REFUNDED = "REFUNDED", "Refunded"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED", "Partially Refunded"
    RECONCILED = "RECONCILED", "Reconciled"


class PaymentMethod(models.TextChoices):
    CASH = "CASH", "Cash"
    MOBILE_MONEY = "MOBILE_MONEY", "Mobile Money"
    CARD = "CARD", "Card"
    BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
    PAYSTACK = "PAYSTACK", "Paystack"
    STRIPE = "STRIPE", "Stripe"
    FLUTTERWAVE = "FLUTTERWAVE", "Flutterwave"


class Currency(models.TextChoices):
    GHS = "GHS", "Ghana Cedi"
    USD = "USD", "US Dollar"
    EUR = "EUR", "Euro"
    GBP = "GBP", "British Pound"
    NGN = "NGN", "Nigerian Naira"
    KES = "KES", "Kenyan Shilling"


class InvoiceAction(models.TextChoices):
    CREATED = "CREATED", "Created"
    PENDING_MANAGER_APPROVAL = (
        "PENDING_MANAGER_APPROVAL",
        "Pending Manager Approval",
    )
    PENDING_FINANCE_APPROVAL = (
        "PENDING_FINANCE_APPROVAL",
        "Pending Finance Approval",
    )
    PENDING_DIRECTOR_APPROVAL = (
        "PENDING_DIRECTOR_APPROVAL",
        "Pending Director Approval",
    )
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    SENT = "SENT", "Sent"
    VIEWED = "VIEWED", "Viewed"
    PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
    PAID = "PAID", "Paid"
    OVERDUE = "OVERDUE", "Overdue"
    CANCELLED = "CANCELLED", "Cancelled"
    VOID = "VOID", "Void"
    REOPENED = "REOPENED", "Reopened"
    LATE_FEE_APPLIED = "LATE_FEE_APPLIED", "Late Fee Applied"


class TaxType(models.TextChoices):
    VAT = "VAT", "Value Added Tax"
    NHIL = "NHIL", "National Health Insurance Levy"
    GETFUND = "GETFUND", "GETFund"
    COVID = "COVID", "COVID Levy"
    ZERO = "ZERO", "Zero Rated"
    EXEMPT = "EXEMPT", "Exempt"
    OTHER = "OTHER", "Other"


class LedgerAccountType(models.TextChoices):
    ASSET = "ASSET", "Asset"
    LIABILITY = "LIABILITY", "Liability"
    EQUITY = "EQUITY", "Equity"
    REVENUE = "REVENUE", "Revenue"
    EXPENSE = "EXPENSE", "Expense"


class ApprovalLevel(models.TextChoices):
    MANAGER = "MANAGER", "Manager"
    FINANCE = "FINANCE", "Finance"
    DIRECTOR = "DIRECTOR", "Director"


# ============================================================
# BASE MODELS
# ============================================================

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


# ============================================================
# INVOICE SEQUENCE
# ============================================================

class InvoiceSequence(models.Model):
    prefix = models.CharField(max_length=10)
    year = models.PositiveIntegerField()
    current_number = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["prefix", "year"],
                name="unique_invoice_sequence_prefix_year",
            )
        ]
        ordering = ["prefix", "year"]

    def __str__(self):
        return f"{self.prefix}-{self.year}: {self.current_number}"

    @classmethod
    def get_next_number(cls, prefix, year):
        with transaction.atomic():
            sequence, _ = cls.objects.select_for_update().get_or_create(
                prefix=prefix,
                year=year,
                defaults={"current_number": 0},
            )

            sequence.current_number += 1
            sequence.save(update_fields=["current_number"])

            return sequence.current_number


# ============================================================
# BILLING CONFIGURATION
# ============================================================

class BillingConfig(TimeStampedModel):
    currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
        default=Currency.GHS,
    )

    default_tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    invoice_prefix = models.CharField(
        max_length=20,
        default="INV",
    )

    payment_terms = models.TextField(
        default="Payment is due within 30 days of invoice date."
    )

    late_fee_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    is_active = models.BooleanField(default=True)

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="billing_configs",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=Q(is_active=True),
                name="one_active_billing_config",
            )
        ]

    def __str__(self):
        return f"Billing Config ({self.currency})"


# ============================================================
# TAX
# ============================================================

class Tax(TimeStampedModel):
    name = models.CharField(max_length=100)

    tax_type = models.CharField(
        max_length=20,
        choices=TaxType.choices,
        default=TaxType.VAT,
    )

    rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    is_active = models.BooleanField(default=True)

    effective_from = models.DateField(default=timezone.now)
    effective_to = models.DateField(null=True, blank=True)

    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-effective_from"]
        indexes = [
            models.Index(fields=["tax_type", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.rate}%)"


# ============================================================
# EXCHANGE RATE
# ============================================================

class ExchangeRate(TimeStampedModel):
    base_currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
    )

    target_currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
    )

    rate = models.DecimalField(
        max_digits=12,
        decimal_places=4,
    )

    effective_date = models.DateField(default=timezone.now)

    source = models.CharField(
        max_length=100,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "base_currency",
                    "target_currency",
                    "effective_date",
                ],
                name="unique_exchange_rate_per_day",
            )
        ]

        ordering = ["-effective_date"]

        indexes = [
            models.Index(
                fields=[
                    "base_currency",
                    "target_currency",
                    "effective_date",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"1 {self.base_currency} = "
            f"{self.rate} {self.target_currency}"
        )


# ============================================================
# INVOICE TEMPLATE
# ============================================================

class InvoiceTemplate(TimeStampedModel):
    name = models.CharField(max_length=100)

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="invoice_templates",
    )

    logo = models.ImageField(
        upload_to="invoice_templates/logos/",
        blank=True,
        null=True,
    )

    footer_text = models.TextField(blank=True)

    brand_color = models.CharField(
        max_length=7,
        default="#1a237e",
    )

    payment_terms = models.TextField(blank=True)

    watermark_text = models.CharField(
        max_length=100,
        blank=True,
    )

    is_default = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "is_default"],
                condition=Q(is_default=True),
                name="unique_default_template_per_org",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


# ============================================================
# INVOICE
# ============================================================

class Invoice(TimeStampedModel, SoftDeleteModel):

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        blank=True,
    )

    public_token = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        db_index=True,
    )

    # --------------------------------------------------------
    # MULTI-TENANT
    # --------------------------------------------------------

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="invoices",
        null=True,
        blank=True,
        db_index=True,
    )

    branch = models.CharField(
        max_length=100,
        blank=True,
    )

    department = models.CharField(
        max_length=100,
        blank=True,
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="invoices",
    )

    incident = models.ForeignKey(
        "incidents.Incident",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_invoices",
    )

    # --------------------------------------------------------
    # TYPE / STATUS
    # --------------------------------------------------------

    invoice_type = models.CharField(
        max_length=20,
        choices=InvoiceType.choices,
        default=InvoiceType.STANDARD,
    )

    status = models.CharField(
        max_length=30,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        db_index=True,
    )

    # --------------------------------------------------------
    # BILLING SNAPSHOT
    # --------------------------------------------------------

    billing_name = models.CharField(
        max_length=255,
        blank=True,
    )

    billing_address = models.TextField(blank=True)

    billing_phone = models.CharField(
        max_length=20,
        blank=True,
    )

    billing_email = models.EmailField(blank=True)

    billing_tax_id = models.CharField(
        max_length=50,
        blank=True,
    )

    billing_organization = models.CharField(
        max_length=255,
        blank=True,
    )

    # --------------------------------------------------------
    # DATES
    # --------------------------------------------------------

    issued_date = models.DateField(
        default=timezone.now,
        db_index=True,
    )

    due_date = models.DateField(db_index=True)

    paid_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    pdf_generated_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    emailed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    last_viewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # --------------------------------------------------------
    # EMAIL TRACKING
    # --------------------------------------------------------

    email_status = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ("PENDING", "Pending"),
            ("SENT", "Sent"),
            ("BOUNCED", "Bounced"),
            ("OPENED", "Opened"),
        ],
        db_index=True,
    )

    email_opened_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    email_bounced_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    email_sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_invoices",
    )

    # --------------------------------------------------------
    # FINANCIAL TOTALS
    # --------------------------------------------------------

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    materials_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total cost of materials purchased for the customer.",
    )

    transport_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Cost of transportation/delivery for this invoice.",
    )

    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    balance_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    original_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    # --------------------------------------------------------
    # CURRENCY
    # --------------------------------------------------------

    currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
        default=Currency.GHS,
        db_index=True,
    )

    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal("1.0000"),
    )

    base_currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
        default=Currency.GHS,
    )

    converted_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    version = models.PositiveIntegerField(default=1)

    # --------------------------------------------------------
    # LATE FEES
    # --------------------------------------------------------

    late_fee_applied = models.BooleanField(default=False)

    late_fee_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    # --------------------------------------------------------
    # NOTES / DOCUMENTS
    # --------------------------------------------------------

    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True)

    pdf_file = models.FileField(
        upload_to="invoices/pdfs/",
        blank=True,
        null=True,
    )

    tags = models.ManyToManyField(
        "InvoiceTag",
        blank=True,
    )

    # --------------------------------------------------------
    # PAYSTACK
    # --------------------------------------------------------

    paystack_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        help_text="Paystack transaction reference.",
    )

    paystack_access_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Paystack access code for checkout.",
    )

    # --------------------------------------------------------
    # FIELD TRACKER
    # --------------------------------------------------------

    tracker = FieldTracker(
        fields=["status"]
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["customer", "status"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["invoice_type"]),
            models.Index(fields=["organization"]),
            models.Index(fields=["public_token"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["currency"]),
            models.Index(fields=["email_status"]),
            models.Index(fields=["paystack_reference"]),
            models.Index(fields=["transport_cost"]),
        ]

        constraints = [
            models.CheckConstraint(
                check=Q(grand_total__gte=0),
                name="invoice_grand_total_positive",
            ),
            models.CheckConstraint(
                check=Q(tax_amount__gte=0),
                name="invoice_tax_positive",
            ),
            models.CheckConstraint(
                check=Q(discount_amount__gte=0),
                name="invoice_discount_positive",
            ),
            models.CheckConstraint(
                check=Q(amount_paid__gte=0),
                name="invoice_amount_paid_positive",
            ),
            models.CheckConstraint(
                check=Q(balance_due__gte=0),
                name="invoice_balance_due_positive",
            ),
            models.CheckConstraint(
                check=Q(amount_paid__lte=F("grand_total")),
                name="invoice_amount_paid_not_exceed_total",
            ),
            models.CheckConstraint(
                check=Q(transport_cost__gte=0),
                name="invoice_transport_cost_positive",
            ),
        ]

        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    # ========================================================
    # STRING / PROPERTIES
    # ========================================================

    def __str__(self):
        customer_name = getattr(
            self.customer,
            "name",
            "Customer",
        )
        return f"{self.invoice_number} - {customer_name}"

    @property
    def is_paid(self):
        return self.status == InvoiceStatus.PAID

    @property
    def is_overdue(self):
        if self.status in [
            InvoiceStatus.PAID,
            InvoiceStatus.CANCELLED,
            InvoiceStatus.VOID,
        ]:
            return False

        if not self.due_date:
            return False

        return timezone.now().date() > self.due_date

    @property
    def is_fully_paid(self):
        return self.balance_due <= Decimal("0")

    @property
    def total_credit_notes(self):
        return (
            self.credit_notes.filter(
                status="ACTIVE"
            ).aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0")
        )

    @property
    def amount_in_smallest_unit(self):
        return int(
            (self.grand_total * Decimal("100"))
            .quantize(Decimal("1"))
        )

    @property
    def amount_in_cents(self):
        return self.amount_in_smallest_unit

    @property
    def materials(self):
        return list(
            self.purchased_items.values(
                "id",
                "description",
                "quantity",
                "unit_cost",
                "total_cost",
            )
        )

    # ========================================================
    # SAVE
    # ========================================================

    def save(self, *args, **kwargs):
        recalc_totals = kwargs.pop(
            "recalc_totals",
            True,
        )

        is_new = self._state.adding

        # ----------------------------------------------------
        # Invoice number
        # ----------------------------------------------------

        if not self.invoice_number:
            prefix_map = {
                InvoiceType.STANDARD: "INV",
                InvoiceType.PROFORMA: "PRO",
                InvoiceType.CREDIT_NOTE: "CN",
                InvoiceType.DEBIT_NOTE: "DN",
            }

            prefix = prefix_map.get(
                self.invoice_type,
                "INV",
            )

            year = timezone.now().year

            number = InvoiceSequence.get_next_number(
                prefix,
                year,
            )

            self.invoice_number = (
                f"{prefix}-{year}-{number:06d}"
            )

        # ----------------------------------------------------
        # Public token
        # ----------------------------------------------------

        if not self.public_token:
            self.public_token = secrets.token_urlsafe(32)

        # ----------------------------------------------------
        # Original total
        # ----------------------------------------------------

        if (
            not self.original_total
            and not is_new
            and self.pk
        ):
            aggregate = self.items.aggregate(
                subtotal=Sum("line_subtotal"),
                tax=Sum("tax_amount"),
            )

            subtotal = (
                aggregate.get("subtotal")
                or Decimal("0")
            )

            tax = (
                aggregate.get("tax")
                or Decimal("0")
            )

            raw = (
                subtotal
                + tax
                + self.materials_total
                + self.transport_cost
                - self.discount_amount
            )

            self.original_total = max(
                Decimal("0"),
                raw,
            )

        # ----------------------------------------------------
        # Calculate totals
        # ----------------------------------------------------

        if recalc_totals and not is_new and self.pk:
            self.calculate_totals()

        # ----------------------------------------------------
        # Payment date
        # ----------------------------------------------------

        if (
            self.status == InvoiceStatus.PAID
            and not self.paid_date
        ):
            self.paid_date = timezone.now().date()

        # ----------------------------------------------------
        # Version
        # ----------------------------------------------------

        if not is_new:
            self.version += 1

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        self.full_clean()

        super().save(*args, **kwargs)

    # ========================================================
    # VALIDATION
    # ========================================================

    def clean(self):
        errors = {}

        if (
            self.due_date
            and self.issued_date
            and self.due_date < self.issued_date
        ):
            errors["due_date"] = (
                "Due date must be on or after issued date."
            )

        if self.grand_total < 0:
            errors["grand_total"] = (
                "Total cannot be negative."
            )

        if self.amount_paid > self.grand_total:
            errors["amount_paid"] = (
                "Amount paid cannot exceed total."
            )

        if self.transport_cost < 0:
            errors["transport_cost"] = (
                "Transport cost cannot be negative."
            )

        if errors:
            raise ValidationError(errors)

    # ========================================================
    # CALCULATE TOTALS
    # ========================================================

    def calculate_totals(self):
        item_aggregate = self.items.aggregate(
            subtotal=Sum("line_subtotal"),
            tax=Sum("tax_amount"),
        )

        self.subtotal = (
            item_aggregate.get("subtotal")
            or Decimal("0")
        )

        self.tax_amount = (
            item_aggregate.get("tax")
            or Decimal("0")
        )

        material_aggregate = self.purchased_items.aggregate(
            total=Sum("total_cost")
        )

        self.materials_total = (
            material_aggregate.get("total")
            or Decimal("0")
        )

        raw_total = (
            self.subtotal
            + self.tax_amount
            - self.discount_amount
            + self.materials_total
            + self.transport_cost
        )

        raw_total = max(
            Decimal("0"),
            raw_total,
        )

        if (
            not self.original_total
            or self.original_total == Decimal("0")
        ):
            self.original_total = raw_total

        credit_total = self.total_credit_notes

        if credit_total > 0:
            self.grand_total = max(
                Decimal("0"),
                raw_total - credit_total,
            )
        else:
            self.grand_total = raw_total

        self.balance_due = (
            self.grand_total
            - self.amount_paid
        )

        if self.balance_due < 0:
            self.balance_due = Decimal("0")

        # ----------------------------------------------------
        # Exchange rate
        # ----------------------------------------------------

        if (
            self.base_currency
            and self.currency
            and self.base_currency != self.currency
        ):
            latest_rate = (
                ExchangeRate.objects.filter(
                    base_currency=self.base_currency,
                    target_currency=self.currency,
                )
                .order_by("-effective_date")
                .first()
            )

            if latest_rate:
                self.exchange_rate = latest_rate.rate

        elif self.base_currency == self.currency:
            self.exchange_rate = Decimal("1.0000")

        self.converted_total = (
            self.grand_total
            * self.exchange_rate
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        return self.grand_total

    # ========================================================
    # SAVE TOTALS
    # ========================================================

    def save_totals(self):
        if not self.pk:
            return

        Invoice.all_objects.filter(
            pk=self.pk
        ).update(
            subtotal=self.subtotal,
            tax_amount=self.tax_amount,
            materials_total=self.materials_total,
            transport_cost=self.transport_cost,
            original_total=self.original_total,
            grand_total=self.grand_total,
            balance_due=self.balance_due,
            converted_total=self.converted_total,
        )

        self.refresh_from_db()

    # ========================================================
    # PAYMENT TOTAL
    # ========================================================

    def update_paid_amount(self):
        total_paid = (
            self.payment_allocations.aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0")
        )

        self.amount_paid = total_paid

        self.balance_due = (
            self.grand_total
            - self.amount_paid
        )

        if self.balance_due < 0:
            self.balance_due = Decimal("0")

        if (
            self.balance_due <= 0
            and self.amount_paid > 0
        ):
            new_status = InvoiceStatus.PAID
            self.paid_date = timezone.now().date()
            self.late_fee_applied = False

        elif self.amount_paid > 0:
            new_status = InvoiceStatus.PARTIALLY_PAID

        else:
            new_status = self.status

        Invoice.all_objects.filter(
            pk=self.pk
        ).update(
            amount_paid=self.amount_paid,
            balance_due=self.balance_due,
            status=new_status,
            paid_date=self.paid_date,
            late_fee_applied=self.late_fee_applied,
        )

        self.refresh_from_db()

        return self

    # ========================================================
    # LATE FEE
    # ========================================================

    def apply_late_fee(self):
        if (
            not self.is_overdue
            or self.late_fee_applied
            or self.balance_due <= 0
        ):
            return Decimal("0")

        config = (
            BillingConfig.objects
            .filter(
                is_active=True,
                organization=self.organization,
            )
            .first()
        )

        if not config:
            config = (
                BillingConfig.objects
                .filter(is_active=True)
                .first()
            )

        if (
            not config
            or config.late_fee_percent <= 0
        ):
            return Decimal("0")

        fee = (
            self.balance_due
            * config.late_fee_percent
            / Decimal("100")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        self.late_fee_amount = fee
        self.grand_total += fee
        self.balance_due += fee
        self.late_fee_applied = True

        Invoice.all_objects.filter(
            pk=self.pk
        ).update(
            grand_total=self.grand_total,
            balance_due=self.balance_due,
            late_fee_amount=self.late_fee_amount,
            late_fee_applied=True,
        )

        self.refresh_from_db()

        InvoiceHistory.objects.create(
            invoice=self,
            action=InvoiceAction.LATE_FEE_APPLIED,
            reason=f"Late fee of {fee} applied.",
        )

        return fee

    # ========================================================
    # STATUS STATE MACHINE
    # ========================================================

    def transition_status(
        self,
        new_status,
        user=None,
        reason=None,
    ):
        valid_transitions = {
            InvoiceStatus.DRAFT: [
                InvoiceStatus.SENT,
                InvoiceStatus.PENDING_MANAGER_APPROVAL,
                InvoiceStatus.CANCELLED,
                InvoiceStatus.VOID,
            ],

            InvoiceStatus.PENDING_MANAGER_APPROVAL: [
                InvoiceStatus.PENDING_FINANCE_APPROVAL,
                InvoiceStatus.APPROVED,
                InvoiceStatus.CANCELLED,
            ],

            InvoiceStatus.PENDING_FINANCE_APPROVAL: [
                InvoiceStatus.PENDING_DIRECTOR_APPROVAL,
                InvoiceStatus.APPROVED,
                InvoiceStatus.CANCELLED,
            ],

            InvoiceStatus.PENDING_DIRECTOR_APPROVAL: [
                InvoiceStatus.APPROVED,
                InvoiceStatus.CANCELLED,
            ],

            InvoiceStatus.APPROVED: [
                InvoiceStatus.SENT,
                InvoiceStatus.CANCELLED,
            ],

            InvoiceStatus.SENT: [
                InvoiceStatus.VIEWED,
                InvoiceStatus.PARTIALLY_PAID,
                InvoiceStatus.PAID,
                InvoiceStatus.OVERDUE,
                InvoiceStatus.CANCELLED,
            ],

            InvoiceStatus.VIEWED: [
                InvoiceStatus.PARTIALLY_PAID,
                InvoiceStatus.PAID,
                InvoiceStatus.OVERDUE,
            ],

            InvoiceStatus.PARTIALLY_PAID: [
                InvoiceStatus.PAID,
                InvoiceStatus.OVERDUE,
            ],

            InvoiceStatus.OVERDUE: [
                InvoiceStatus.PAID,
                InvoiceStatus.CANCELLED,
            ],

            InvoiceStatus.PAID: [],

            InvoiceStatus.CANCELLED: [],

            InvoiceStatus.VOID: [],
        }

        if new_status not in valid_transitions.get(
            self.status,
            [],
        ):
            raise ValidationError(
                f"Cannot transition from "
                f"'{self.status}' to "
                f"'{new_status}'."
            )

        old_status = self.status

        with transaction.atomic():

            self.status = new_status

            if (
                new_status == InvoiceStatus.APPROVED
                and user
            ):
                self.approved_at = timezone.now()

            if (
                new_status == InvoiceStatus.SENT
                and user
            ):
                self.emailed_at = timezone.now()
                self.email_sent_by = user

            self.version += 1

            self.save(
                update_fields=[
                    "status",
                    "approved_at",
                    "emailed_at",
                    "email_sent_by",
                    "version",
                    "updated_at",
                ],
                recalc_totals=False,
            )

            # ------------------------------------------------
            # History
            # ------------------------------------------------

            action_map = {
                InvoiceStatus.DRAFT:
                    InvoiceAction.CREATED,

                InvoiceStatus.PENDING_MANAGER_APPROVAL:
                    InvoiceAction.PENDING_MANAGER_APPROVAL,

                InvoiceStatus.PENDING_FINANCE_APPROVAL:
                    InvoiceAction.PENDING_FINANCE_APPROVAL,

                InvoiceStatus.PENDING_DIRECTOR_APPROVAL:
                    InvoiceAction.PENDING_DIRECTOR_APPROVAL,

                InvoiceStatus.APPROVED:
                    InvoiceAction.APPROVED,

                InvoiceStatus.SENT:
                    InvoiceAction.SENT,

                InvoiceStatus.VIEWED:
                    InvoiceAction.VIEWED,

                InvoiceStatus.PARTIALLY_PAID:
                    InvoiceAction.PARTIALLY_PAID,

                InvoiceStatus.PAID:
                    InvoiceAction.PAID,

                InvoiceStatus.OVERDUE:
                    InvoiceAction.OVERDUE,

                InvoiceStatus.CANCELLED:
                    InvoiceAction.CANCELLED,

                InvoiceStatus.VOID:
                    InvoiceAction.VOID,
            }

            action = action_map.get(
                new_status,
                InvoiceAction.CREATED,
            )

            InvoiceHistory.objects.create(
                invoice=self,
                action=action,
                user=user,
                reason=(
                    reason
                    or
                    f"Status changed from "
                    f"{old_status} to {new_status}"
                ),
                old_status=old_status,
                new_status=new_status,
                metadata={
                    "ip": getattr(
                        user,
                        "last_login_ip",
                        None,
                    )
                    if user
                    else None,
                    "user_agent": None,
                },
            )

            # ------------------------------------------------
            # Audit
            # ------------------------------------------------

            try:
                from audit.services import AuditService

                AuditService.log(
                    action=f"INVOICE_{new_status}",
                    user=user,
                    instance=self,
                    module="billing",
                    description=(
                        f"Invoice "
                        f"{self.invoice_number} "
                        f"status changed to "
                        f"{new_status}"
                    ),
                    request=None,
                )

            except (ImportError, AttributeError):
                pass

            # ------------------------------------------------
            # Accounting
            # ------------------------------------------------

            if new_status == InvoiceStatus.APPROVED:
                self.create_journal_entry()

            if new_status == InvoiceStatus.PAID:
                self.create_payment_journal_entry()

        # ----------------------------------------------------
        # Send email AFTER transaction
        # ----------------------------------------------------

        if new_status == InvoiceStatus.SENT:

            try:
                from .utils import send_invoice_email

                recipient_email = getattr(
                    self.customer,
                    "email",
                    None,
                )

                if (
                    recipient_email
                    and self.grand_total > 0
                ):
                    success = send_invoice_email(
                        self,
                        recipient_email,
                    )

                    if success:
                        Invoice.all_objects.filter(
                            pk=self.pk
                        ).update(
                            email_status="SENT",
                            emailed_at=timezone.now(),
                        )

                    else:
                        Invoice.all_objects.filter(
                            pk=self.pk
                        ).update(
                            email_status="PENDING",
                        )

            except Exception:
                Invoice.all_objects.filter(
                    pk=self.pk
                ).update(
                    email_status="PENDING"
                )

        return self

    # ========================================================
    # JOURNAL ENTRY
    # ========================================================

    def create_journal_entry(self):
        try:
            ar_account = (
                LedgerAccount.objects.filter(
                    account_type=LedgerAccountType.ASSET,
                    organization=self.organization,
                    is_active=True,
                )
                .filter(
                    Q(name__icontains="receivable")
                    | Q(code__startswith="12")
                )
                .first()
            )

            if not ar_account:
                ar_account = (
                    LedgerAccount.objects.filter(
                        account_type=LedgerAccountType.ASSET,
                        organization=self.organization,
                        is_active=True,
                    ).first()
                )

            revenue_account = (
                LedgerAccount.objects.filter(
                    account_type=LedgerAccountType.REVENUE,
                    organization=self.organization,
                    is_active=True,
                )
                .first()
            )

            if (
                not ar_account
                or not revenue_account
            ):
                return None

            journal_entry = JournalEntry.objects.create(
                description=(
                    f"Invoice "
                    f"{self.invoice_number} approved"
                ),
                invoice=self,
                posted_at=timezone.now(),
            )

            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=ar_account,
                debit=self.grand_total,
                credit=Decimal("0"),
                description=(
                    f"Invoice "
                    f"{self.invoice_number} "
                    f"- Accounts Receivable"
                ),
            )

            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=revenue_account,
                debit=Decimal("0"),
                credit=self.grand_total,
                description=(
                    f"Invoice "
                    f"{self.invoice_number} "
                    f"- Revenue"
                ),
            )

            return journal_entry

        except Exception:
            return None

    # ========================================================
    # PAYMENT JOURNAL
    # ========================================================

    def create_payment_journal_entry(self):
        try:
            cash_account = (
                LedgerAccount.objects.filter(
                    account_type=LedgerAccountType.ASSET,
                    organization=self.organization,
                    is_active=True,
                )
                .exclude(
                    name__icontains="receivable"
                )
                .first()
            )

            ar_account = (
                LedgerAccount.objects.filter(
                    account_type=LedgerAccountType.ASSET,
                    organization=self.organization,
                    is_active=True,
                )
                .filter(
                    Q(name__icontains="receivable")
                    | Q(code__startswith="12")
                )
                .first()
            )

            if not ar_account:
                ar_account = (
                    LedgerAccount.objects.filter(
                        account_type=LedgerAccountType.ASSET,
                        organization=self.organization,
                        is_active=True,
                    ).first()
                )

            if (
                not cash_account
                or not ar_account
            ):
                return None

            journal_entry = JournalEntry.objects.create(
                description=(
                    f"Payment for invoice "
                    f"{self.invoice_number}"
                ),
                invoice=self,
                posted_at=timezone.now(),
            )

            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=cash_account,
                debit=self.amount_paid,
                credit=Decimal("0"),
                description=(
                    f"Invoice "
                    f"{self.invoice_number} "
                    f"- Cash"
                ),
            )

            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=ar_account,
                debit=Decimal("0"),
                credit=self.amount_paid,
                description=(
                    f"Invoice "
                    f"{self.invoice_number} "
                    f"- Accounts Receivable"
                ),
            )

            return journal_entry

        except Exception:
            return None

    # ========================================================
    # REFUND JOURNAL
    # ========================================================

    def create_refund_journal_entry(
        self,
        refund_amount,
    ):
        try:
            refund_account = (
                LedgerAccount.objects.filter(
                    account_type=LedgerAccountType.EXPENSE,
                    organization=self.organization,
                    is_active=True,
                ).first()
            )

            cash_account = (
                LedgerAccount.objects.filter(
                    account_type=LedgerAccountType.ASSET,
                    organization=self.organization,
                    is_active=True,
                )
                .exclude(
                    name__icontains="receivable"
                )
                .first()
            )

            if (
                not refund_account
                or not cash_account
            ):
                return None

            journal_entry = JournalEntry.objects.create(
                description=(
                    f"Refund for invoice "
                    f"{self.invoice_number}"
                ),
                invoice=self,
                posted_at=timezone.now(),
            )

            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=refund_account,
                debit=refund_amount,
                credit=Decimal("0"),
                description=(
                    f"Invoice "
                    f"{self.invoice_number} "
                    f"- Refund"
                ),
            )

            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=cash_account,
                debit=Decimal("0"),
                credit=refund_amount,
                description=(
                    f"Invoice "
                    f"{self.invoice_number} "
                    f"- Cash"
                ),
            )

            return journal_entry

        except Exception:
            return None

    # ========================================================
    # CONVENIENCE METHODS
    # ========================================================

    def mark_sent(self, user=None):
        return self.transition_status(
            InvoiceStatus.SENT,
            user,
        )

    def mark_approved(self, user=None):
        return self.transition_status(
            InvoiceStatus.APPROVED,
            user,
        )

    def mark_paid(self):
        if (
            self.balance_due <= 0
            and self.amount_paid > 0
        ):
            old_status = self.status

            self.status = InvoiceStatus.PAID
            self.paid_date = timezone.now().date()
            self.late_fee_applied = False
            self.version += 1

            Invoice.all_objects.filter(
                pk=self.pk
            ).update(
                status=self.status,
                paid_date=self.paid_date,
                late_fee_applied=False,
                version=self.version,
            )

            InvoiceHistory.objects.create(
                invoice=self,
                action=InvoiceAction.PAID,
                old_status=old_status,
                new_status=InvoiceStatus.PAID,
                reason="Invoice fully paid.",
            )

            self.create_payment_journal_entry()

            self.refresh_from_db()

        return self

    def mark_overdue(self):
        if (
            self.is_overdue
            and self.status not in [
                InvoiceStatus.PAID,
                InvoiceStatus.CANCELLED,
                InvoiceStatus.VOID,
            ]
        ):
            return self.transition_status(
                InvoiceStatus.OVERDUE,
                reason="Payment overdue.",
            )

        return self

    def cancel(
        self,
        user=None,
        reason=None,
    ):
        if self.status in [
            InvoiceStatus.PAID,
            InvoiceStatus.CANCELLED,
            InvoiceStatus.VOID,
        ]:
            raise ValidationError(
                "Cannot cancel a paid, cancelled, "
                "or void invoice."
            )

        return self.transition_status(
            InvoiceStatus.CANCELLED,
            user,
            reason,
        )

    def get_aging_category(self):
        if self.status == InvoiceStatus.PAID:
            return "PAID"

        if self.status == InvoiceStatus.CANCELLED:
            return "CANCELLED"

        if self.status == InvoiceStatus.VOID:
            return "VOID"

        if not self.due_date:
            return "CURRENT"

        days_due = (
            timezone.now().date()
            - self.due_date
        ).days

        if days_due <= 0:
            return "CURRENT"

        if days_due <= 30:
            return "1-30_DAYS"

        if days_due <= 60:
            return "31-60_DAYS"

        if days_due <= 90:
            return "61-90_DAYS"

        return "90+_DAYS"


# ============================================================
# INVOICE HISTORY
# ============================================================

class InvoiceHistory(TimeStampedModel):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="history",
    )

    action = models.CharField(
        max_length=30,
        choices=InvoiceAction.choices,
        db_index=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    reason = models.TextField(blank=True)

    old_status = models.CharField(
        max_length=30,
        blank=True,
    )

    new_status = models.CharField(
        max_length=30,
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["invoice", "created_at"]
            ),
            models.Index(fields=["action"]),
            models.Index(fields=["created_at"]),
        ]

        verbose_name_plural = "Invoice Histories"


# ============================================================
# INVOICE TAG
# ============================================================

class InvoiceTag(TimeStampedModel):
    name = models.CharField(
        max_length=50,
        unique=True,
    )

    color = models.CharField(
        max_length=7,
        default="#6c757d",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# ============================================================
# INVOICE COMMENT
# ============================================================

class InvoiceComment(TimeStampedModel):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    text = models.TextField()

    is_internal = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return (
            f"{self.invoice.invoice_number} "
            f"- Comment by {self.user}"
        )


# ============================================================
# INVOICE APPROVAL
# ============================================================

class InvoiceApproval(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="approvals",
    )

    level = models.CharField(
        max_length=20,
        choices=ApprovalLevel.choices,
    )

    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("APPROVED", "Approved"),
            ("REJECTED", "Rejected"),
        ],
        default="PENDING",
    )

    comments = models.TextField(blank=True)

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["level"]

        constraints = [
            models.UniqueConstraint(
                fields=["invoice", "level"],
                name="unique_invoice_approval_level",
            )
        ]

        verbose_name_plural = "Invoice Approvals"

    def __str__(self):
        return (
            f"{self.invoice.invoice_number} "
            f"- {self.level}"
        )

    def approve(self):
        with transaction.atomic():

            self.status = "APPROVED"
            self.approved_at = timezone.now()
            self.save(
                update_fields=[
                    "status",
                    "approved_at",
                    "updated_at",
                ]
            )

            approvals = self.invoice.approvals.all()

            if (
                approvals.exists()
                and not approvals.exclude(
                    status="APPROVED"
                ).exists()
            ):
                if self.invoice.status in [
                    InvoiceStatus.PENDING_MANAGER_APPROVAL,
                    InvoiceStatus.PENDING_FINANCE_APPROVAL,
                    InvoiceStatus.PENDING_DIRECTOR_APPROVAL,
                ]:
                    self.invoice.mark_approved(
                        self.approver
                    )

    def reject(self, reason):
        with transaction.atomic():

            self.status = "REJECTED"
            self.comments = reason

            self.save(
                update_fields=[
                    "status",
                    "comments",
                    "updated_at",
                ]
            )

            if self.invoice.status not in [
                InvoiceStatus.CANCELLED,
                InvoiceStatus.PAID,
                InvoiceStatus.VOID,
            ]:
                self.invoice.transition_status(
                    InvoiceStatus.CANCELLED,
                    self.approver,
                    f"Rejected at {self.level}: {reason}",
                )


# ============================================================
# INVOICE ITEM
# ============================================================

class InvoiceItem(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items",
    )

    description = models.CharField(
        max_length=255
    )

    sku = models.CharField(
        max_length=100,
        blank=True,
    )

    unit = models.CharField(
        max_length=20,
        blank=True,
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        validators=[
            MinValueValidator(
                Decimal("0.01")
            )
        ],
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0"))
        ],
    )

    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("100")),
        ],
    )

    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(Decimal("0"))
        ],
    )

    tax = models.ForeignKey(
        Tax,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoice_items",
    )

    taxes = models.ManyToManyField(
        Tax,
        blank=True,
        through="InvoiceItemTax",
    )

    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(Decimal("0"))
        ],
    )

    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(Decimal("0"))
        ],
    )

    line_subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        validators=[
            MinValueValidator(Decimal("0"))
        ],
    )

    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        validators=[
            MinValueValidator(Decimal("0"))
        ],
    )

    incident = models.ForeignKey(
        "incidents.Incident",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoice_items",
    )

    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoice_items",
    )

    class Meta:
        ordering = ["created_at"]

        indexes = [
            models.Index(fields=["invoice"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["created_at"]),
        ]

        verbose_name_plural = "Invoice Items"

    def __str__(self):
        return (
            f"{self.description} - "
            f"{self.line_total}"
        )

    def save(self, *args, **kwargs):
        self.calculate_totals(
            use_m2m=self.pk is not None
        )

        self.full_clean(
            exclude=[
                "invoice",
            ]
        )

        super().save(*args, **kwargs)

        # M2M tax records may have changed after
        # the item has been saved.
        if self.pk:
            self.calculate_totals(
                use_m2m=True
            )

            InvoiceItem.objects.filter(
                pk=self.pk
            ).update(
                line_subtotal=self.line_subtotal,
                discount_amount=self.discount_amount,
                tax=self.tax,
                tax_rate=self.tax_rate,
                tax_amount=self.tax_amount,
                line_total=self.line_total,
            )

        if self.invoice_id:
            self.invoice.calculate_totals()
            self.invoice.save_totals()

    def delete(self, *args, **kwargs):
        invoice = self.invoice

        super().delete(*args, **kwargs)

        if invoice.pk:
            invoice.calculate_totals()
            invoice.save_totals()

    def calculate_totals(self, use_m2m=True):

        self.line_subtotal = (
            self.quantity
            * self.unit_price
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        self.discount_amount = (
            self.line_subtotal
            * self.discount_percent
            / Decimal("100")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        if self.discount_amount > self.line_subtotal:
            self.discount_amount = (
                self.line_subtotal
            )

        after_discount = (
            self.line_subtotal
            - self.discount_amount
        )

        tax_rate_total = Decimal("0")
        tax_amount_total = Decimal("0")
        first_tax = None

        if (
            use_m2m
            and self.pk
            and hasattr(self, "item_taxes")
        ):
            item_taxes = (
                self.item_taxes
                .select_related("tax")
                .all()
            )

            for item_tax in item_taxes:

                rate = (
                    item_tax.rate_override
                    if item_tax.rate_override is not None
                    else item_tax.tax.rate
                )

                tax_amount = (
                    after_discount
                    * rate
                    / Decimal("100")
                ).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )

                tax_rate_total += rate
                tax_amount_total += tax_amount

                if first_tax is None:
                    first_tax = item_tax.tax

        if first_tax is not None:
            self.tax = first_tax
            self.tax_rate = tax_rate_total
            self.tax_amount = tax_amount_total

        else:
            if self.tax_rate:
                self.tax_amount = (
                    after_discount
                    * self.tax_rate
                    / Decimal("100")
                ).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
            else:
                self.tax_amount = Decimal("0.00")

        self.line_total = (
            after_discount
            + self.tax_amount
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        return self.line_total

    def clean(self):
        errors = {}

        if self.quantity <= 0:
            errors["quantity"] = (
                "Quantity must be greater than zero."
            )

        if self.unit_price < 0:
            errors["unit_price"] = (
                "Unit price cannot be negative."
            )

        if not (
            Decimal("0")
            <= self.discount_percent
            <= Decimal("100")
        ):
            errors["discount_percent"] = (
                "Discount must be between 0 and 100."
            )

        if (
            self.discount_amount
            > self.line_subtotal
        ):
            errors["discount_amount"] = (
                "Discount cannot exceed line subtotal."
            )

        if errors:
            raise ValidationError(errors)


# ============================================================
# INVOICE ITEM TAX
# ============================================================

class InvoiceItemTax(TimeStampedModel):
    item = models.ForeignKey(
        InvoiceItem,
        on_delete=models.CASCADE,
        related_name="item_taxes",
    )

    tax = models.ForeignKey(
        Tax,
        on_delete=models.PROTECT,
    )

    rate_override = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("0"))
        ],
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["item", "tax"],
                name="unique_invoice_item_tax",
            )
        ]

        indexes = [
            models.Index(
                fields=["item", "tax"]
            )
        ]

    def __str__(self):
        return (
            f"{self.item.description} - "
            f"{self.tax.name}"
        )

    def save(self, *args, **kwargs):
        with transaction.atomic():

            rate = (
                self.rate_override
                if self.rate_override is not None
                else self.tax.rate
            )

            after_discount = (
                self.item.line_subtotal
                - self.item.discount_amount
            )

            self.amount = (
                after_discount
                * rate
                / Decimal("100")
            ).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )

            super().save(*args, **kwargs)

            self.item.calculate_totals(
                use_m2m=True
            )

            InvoiceItem.objects.filter(
                pk=self.item.pk
            ).update(
                tax=self.item.tax,
                tax_rate=self.item.tax_rate,
                tax_amount=self.item.tax_amount,
                line_total=self.item.line_total,
            )

            self.item.invoice.calculate_totals()
            self.item.invoice.save_totals()

    def delete(self, *args, **kwargs):
        item = self.item
        invoice = item.invoice

        super().delete(*args, **kwargs)

        item.calculate_totals(
            use_m2m=True
        )

        InvoiceItem.objects.filter(
            pk=item.pk
        ).update(
            tax=item.tax,
            tax_rate=item.tax_rate,
            tax_amount=item.tax_amount,
            line_total=item.line_total,
        )

        invoice.calculate_totals()
        invoice.save_totals()


# ============================================================
# PURCHASED ITEMS / MATERIALS
# ============================================================

class PurchasedItem(TimeStampedModel):
    """
    Items purchased on behalf of the customer,
    such as materials, supplies, spare parts, etc.
    """

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="purchased_items",
    )

    description = models.CharField(
        max_length=255
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        validators=[
            MinValueValidator(
                Decimal("0.01")
            )
        ],
    )

    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0"))
        ],
    )

    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        default=Decimal("0.00"),
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return (
            f"{self.description} "
            f"x{self.quantity}"
        )

    def save(self, *args, **kwargs):
        self.total_cost = (
            self.quantity
            * self.unit_cost
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        super().save(*args, **kwargs)

        if self.invoice_id:
            invoice = self.invoice

            invoice.calculate_totals()

            Invoice.all_objects.filter(
                pk=self.invoice_id
            ).update(
                subtotal=invoice.subtotal,
                tax_amount=invoice.tax_amount,
                materials_total=invoice.materials_total,
                transport_cost=invoice.transport_cost,
                original_total=invoice.original_total,
                grand_total=invoice.grand_total,
                balance_due=invoice.balance_due,
                converted_total=invoice.converted_total,
            )

    def delete(self, *args, **kwargs):
        invoice = self.invoice

        super().delete(*args, **kwargs)

        invoice.calculate_totals()
        invoice.save_totals()


# ============================================================
# PAYMENT INTENT
# ============================================================

class PaymentIntent(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="payment_intents",
    )

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_intents",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal("0.01")
            )
        ],
    )

    currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
        default=Currency.GHS,
    )

    gateway = models.CharField(
        max_length=20,
        default="PAYSTACK",
    )

    gateway_reference = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
    )

    expires_at = models.DateTimeField()

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["customer"]),
            models.Index(
                fields=["gateway_reference"]
            ),
            models.Index(
                fields=["status", "expires_at"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.customer.name} - "
            f"{self.amount} {self.currency}"
        )


# ============================================================
# PAYMENT
# ============================================================

class Payment(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal("0.01")
            )
        ],
    )

    currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
        default=Currency.GHS,
        db_index=True,
    )

    fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(Decimal("0"))
        ],
    )

    net_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0"))
        ],
    )

    method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.PAYSTACK,
    )

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
    )

    gateway = models.CharField(
        max_length=20,
        default="PAYSTACK",
    )

    gateway_reference = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    description = models.CharField(
        max_length=255,
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    refunded_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(Decimal("0"))
        ],
    )

    refund_reference = models.CharField(
        max_length=100,
        blank=True,
    )

    refunded_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    reconciled = models.BooleanField(
        default=False
    )

    reconciled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    bank_statement_reference = models.CharField(
        max_length=100,
        blank=True,
    )

    gateway_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(Decimal("0"))
        ],
    )

    authorization_code = models.CharField(
        max_length=100,
        blank=True,
    )

    customer_code = models.CharField(
        max_length=100,
        blank=True,
    )

    channel = models.CharField(
        max_length=50,
        blank=True,
    )

    bank = models.CharField(
        max_length=100,
        blank=True,
    )

    card_last4 = models.CharField(
        max_length=4,
        blank=True,
    )

    card_type = models.CharField(
        max_length=50,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["customer", "status"]
            ),
            models.Index(
                fields=["gateway_reference"]
            ),
            models.Index(fields=["paid_at"]),
            models.Index(
                fields=["status", "created_at"]
            ),
            models.Index(fields=["currency"]),
        ]

        constraints = [
            models.CheckConstraint(
                check=Q(amount__gte=0),
                name="payment_amount_positive",
            ),
            models.CheckConstraint(
                check=Q(net_amount__gte=0),
                name="payment_net_positive",
            ),
            models.CheckConstraint(
                check=Q(refunded_amount__gte=0),
                name="payment_refunded_amount_positive",
            ),
            models.CheckConstraint(
                check=Q(refunded_amount__lte=F("amount")),
                name="payment_refund_not_exceed_amount",
            ),
        ]

        verbose_name_plural = "Payments"

    def __str__(self):
        return (
            f"{self.customer.name} - "
            f"{self.amount} {self.currency}"
        )

    @property
    def is_successful(self):
        return self.status == PaymentStatus.SUCCESS

    @property
    def refund_balance(self):
        return max(
            Decimal("0"),
            self.amount - self.refunded_amount,
        )

    def save(self, *args, **kwargs):
        self.net_amount = (
            self.amount - self.fee
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        self.full_clean()

        super().save(*args, **kwargs)

    def clean(self):
        errors = {}

        if self.fee > self.amount:
            errors["fee"] = (
                "Fee cannot exceed amount."
            )

        if self.refunded_amount > self.amount:
            errors["refunded_amount"] = (
                "Refund cannot exceed payment amount."
            )

        if errors:
            raise ValidationError(errors)

    def mark_successful(
        self,
        gateway_ref=None,
        gateway_response=None,
    ):
        if self.status not in [
            PaymentStatus.PENDING,
            PaymentStatus.INITIATED,
        ]:
            raise ValidationError(
                "Payment must be pending or initiated "
                "to mark successful."
            )

        with transaction.atomic():

            self.status = PaymentStatus.SUCCESS
            self.paid_at = timezone.now()

            if gateway_ref:
                self.gateway_reference = (
                    gateway_ref
                )

            if gateway_response:
                metadata = dict(self.metadata or {})
                metadata["gateway_response"] = (
                    gateway_response
                )
                self.metadata = metadata

            self.save(
                update_fields=[
                    "status",
                    "paid_at",
                    "gateway_reference",
                    "metadata",
                    "updated_at",
                ]
            )

            for allocation in (
                self.allocations.select_related(
                    "invoice"
                ).all()
            ):
                allocation.invoice.update_paid_amount()

        return self

    def mark_failed(
        self,
        gateway_response=None,
    ):
        if self.status == PaymentStatus.SUCCESS:
            raise ValidationError(
                "Cannot mark a successful payment as failed."
            )

        with transaction.atomic():

            self.status = PaymentStatus.FAILED

            if gateway_response:
                metadata = dict(self.metadata or {})
                metadata["gateway_response"] = (
                    gateway_response
                )
                self.metadata = metadata

            self.save(
                update_fields=[
                    "status",
                    "metadata",
                    "updated_at",
                ]
            )

        return self

    def refund(
        self,
        amount=None,
        reason="",
    ):
        if not self.is_successful:
            raise ValidationError(
                "Only successful payments can be refunded."
            )

        refund_amount = (
            amount
            if amount is not None
            else self.amount
        )

        if refund_amount <= 0:
            raise ValidationError(
                "Refund amount must be positive."
            )

        if refund_amount > self.refund_balance:
            raise ValidationError(
                "Refund amount exceeds remaining "
                f"balance of {self.refund_balance}."
            )

        original_refund_amount = refund_amount

        with transaction.atomic():

            allocations = list(
                self.allocations
                .select_related("invoice")
                .select_for_update()
                .all()
            )

            self.refunded_amount += (
                refund_amount
            )

            self.refunded_at = timezone.now()

            self.refund_reference = (
                f"REF-"
                f"{timezone.now().strftime('%Y%m%d')}-"
                f"{uuid.uuid4().hex[:6].upper()}"
            )

            if (
                self.refunded_amount
                >= self.amount
            ):
                self.refunded_amount = self.amount
                self.status = (
                    PaymentStatus.REFUNDED
                )
            else:
                self.status = (
                    PaymentStatus.PARTIALLY_REFUNDED
                )

            self.save(
                update_fields=[
                    "refunded_amount",
                    "refunded_at",
                    "refund_reference",
                    "status",
                    "updated_at",
                ]
            )

            remaining_refund = refund_amount

            for allocation in allocations:

                if remaining_refund <= 0:
                    break

                invoice = allocation.invoice

                refund_allocation = min(
                    remaining_refund,
                    allocation.amount,
                )

                invoice.amount_paid = max(
                    Decimal("0"),
                    invoice.amount_paid
                    - refund_allocation,
                )

                invoice.balance_due = max(
                    Decimal("0"),
                    invoice.grand_total
                    - invoice.amount_paid,
                )

                if (
                    invoice.amount_paid
                    < invoice.grand_total
                    and invoice.status
                    == InvoiceStatus.PAID
                ):
                    invoice.status = (
                        InvoiceStatus.PARTIALLY_PAID
                    )
                    invoice.paid_date = None

                Invoice.all_objects.filter(
                    pk=invoice.pk
                ).update(
                    amount_paid=invoice.amount_paid,
                    balance_due=invoice.balance_due,
                    status=invoice.status,
                    paid_date=invoice.paid_date,
                )

                invoice.create_refund_journal_entry(
                    refund_allocation
                )

                remaining_refund -= (
                    refund_allocation
                )

            # ------------------------------------------------
            # Credit note
            # ------------------------------------------------

            try:
                from .services import CreditNoteService

                CreditNoteService.create_from_refund(
                    self,
                    original_refund_amount,
                    reason,
                )

            except (
                ImportError,
                AttributeError,
            ):
                pass

        return original_refund_amount


# ============================================================
# PAYMENT ALLOCATION
# ============================================================

class PaymentAllocation(TimeStampedModel):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="allocations",
    )

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name="payment_allocations",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal("0.01")
            )
        ],
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["payment"]),
            models.Index(fields=["invoice"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["payment", "invoice"],
                name="unique_payment_invoice_allocation",
            )
        ]

        verbose_name_plural = "Payment Allocations"

    def __str__(self):
        return (
            f"{self.payment.customer.name} - "
            f"{self.invoice.invoice_number}: "
            f"{self.amount}"
        )

    def clean(self):
        if not self.payment_id:
            return

        total_allocated = (
            PaymentAllocation.objects
            .filter(payment=self.payment)
            .exclude(pk=self.pk)
            .aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0")
        )

        if (
            total_allocated + self.amount
            > self.payment.amount
        ):
            raise ValidationError(
                "Total allocations cannot exceed "
                "payment amount."
            )

    def save(self, *args, **kwargs):
        self.full_clean()

        with transaction.atomic():

            Payment.objects.select_for_update().get(
                pk=self.payment.pk
            )

            super().save(*args, **kwargs)

            self.invoice.update_paid_amount()

    def delete(self, *args, **kwargs):
        invoice = self.invoice

        super().delete(*args, **kwargs)

        invoice.update_paid_amount()


# ============================================================
# PAYMENT GATEWAY TRANSACTION
# ============================================================

class PaymentGatewayTransaction(TimeStampedModel):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="gateway_transactions",
    )

    gateway = models.CharField(
        max_length=20,
        default="PAYSTACK",
    )

    reference = models.CharField(
        max_length=100,
        db_index=True,
    )

    payload = models.JSONField(
        default=dict
    )

    response = models.JSONField(
        default=dict
    )

    status = models.CharField(
        max_length=20,
        default="PENDING",
        db_index=True,
    )

    verified = models.BooleanField(
        default=False
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["payment"]),
            models.Index(
                fields=["status", "created_at"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.gateway} - "
            f"{self.reference}"
        )


# ============================================================
# WEBHOOK LOG
# ============================================================

class WebhookLog(TimeStampedModel):
    gateway = models.CharField(
        max_length=20,
        default="PAYSTACK",
    )

    headers = models.JSONField(
        default=dict
    )

    payload = models.JSONField(
        default=dict
    )

    signature = models.CharField(
        max_length=255,
        blank=True,
    )

    verified = models.BooleanField(
        default=False
    )

    processed = models.BooleanField(
        default=False
    )

    retry_count = models.PositiveIntegerField(
        default=0
    )

    status = models.CharField(
        max_length=20,
        default="RECEIVED",
        db_index=True,
    )

    error_message = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["gateway", "created_at"]
            ),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return (
            f"{self.gateway} webhook at "
            f"{self.created_at}"
        )


# ============================================================
# CREDIT NOTE
# ============================================================

class CreditNote(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    credit_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        blank=True,
    )

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name="credit_notes",
    )

    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="credit_notes",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal("0.01")
            )
        ],
    )

    reason = models.TextField()

    currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
        default=Currency.GHS,
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("ACTIVE", "Active"),
            ("USED", "Used"),
            ("EXPIRED", "Expired"),
        ],
        default="ACTIVE",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_credit_notes",
    )

    issued_date = models.DateField(
        default=timezone.now
    )

    expiry_date = models.DateField(
        null=True,
        blank=True,
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["credit_number"]),
            models.Index(
                fields=["invoice", "status"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.credit_number} - "
            f"{self.amount}"
        )

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        if not self.credit_number:
            prefix = "CN"
            year = timezone.now().year

            number = (
                InvoiceSequence.get_next_number(
                    prefix,
                    year,
                )
            )

            self.credit_number = (
                f"{prefix}-{year}-{number:06d}"
            )

        self.full_clean()

        super().save(*args, **kwargs)

        if (
            is_new
            and self.invoice_id
        ):
            self.invoice.calculate_totals()
            self.invoice.save_totals()


# ============================================================
# INVOICE ATTACHMENT
# ============================================================

class InvoiceAttachment(TimeStampedModel):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    file = models.FileField(
        upload_to="invoices/attachments/"
    )

    filename = models.CharField(
        max_length=255,
        blank=True,
    )

    description = models.CharField(
        max_length=255,
        blank=True,
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_invoice_attachments",
    )

    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    mime_type = models.CharField(
        max_length=100,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.invoice.invoice_number} - "
            f"{self.filename or self.file.name}"
        )


# ============================================================
# RECURRING INVOICE
# ============================================================

class RecurringInvoice(TimeStampedModel):

    FREQUENCY_CHOICES = (
        ("DAILY", "Daily"),
        ("WEEKLY", "Weekly"),
        ("MONTHLY", "Monthly"),
        ("QUARTERLY", "Quarterly"),
        ("YEARLY", "Yearly"),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="recurring_invoices",
    )

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="recurring_invoices",
    )

    template = models.ForeignKey(
        InvoiceTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recurring_invoices",
    )

    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default="MONTHLY",
    )

    next_issue_date = models.DateField(
        db_index=True
    )

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    default_subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    default_tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    default_discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
        default=Currency.GHS,
    )

    notes = models.TextField(
        blank=True
    )

    last_generated_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=[
                    "next_issue_date",
                    "is_active",
                ]
            ),
            models.Index(
                fields=[
                    "customer",
                    "is_active",
                ]
            ),
        ]

        verbose_name_plural = "Recurring Invoices"

    def __str__(self):
        return (
            f"{self.customer.name} - "
            f"{self.frequency}"
        )


# ============================================================
# LEDGER ACCOUNT
# ============================================================

class LedgerAccount(TimeStampedModel):
    code = models.CharField(
        max_length=20,
        unique=True,
    )

    name = models.CharField(
        max_length=100
    )

    account_type = models.CharField(
        max_length=20,
        choices=LedgerAccountType.choices,
        db_index=True,
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="ledger_accounts",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    class Meta:
        ordering = ["code"]

        indexes = [
            models.Index(
                fields=[
                    "organization",
                    "is_active",
                ]
            ),
            models.Index(
                fields=[
                    "account_type",
                    "is_active",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.code} - "
            f"{self.name}"
        )


# ============================================================
# JOURNAL ENTRY
# ============================================================

class JournalEntry(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    entry_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        blank=True,
    )

    description = models.TextField()

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_entries",
    )

    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_entries",
    )

    posted_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-posted_at"]

        indexes = [
            models.Index(fields=["posted_at"]),
            models.Index(
                fields=[
                    "invoice",
                    "posted_at",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.entry_number} - "
            f"{self.description}"
        )

    def save(self, *args, **kwargs):
        if not self.entry_number:

            prefix = "JE"
            year = timezone.now().year

            number = (
                InvoiceSequence.get_next_number(
                    prefix,
                    year,
                )
            )

            self.entry_number = (
                f"{prefix}-{year}-{number:06d}"
            )

        super().save(*args, **kwargs)

    @property
    def total_debits(self):
        return (
            self.lines.aggregate(
                total=Sum("debit")
            )["total"]
            or Decimal("0")
        )

    @property
    def total_credits(self):
        return (
            self.lines.aggregate(
                total=Sum("credit")
            )["total"]
            or Decimal("0")
        )

    @property
    def is_balanced(self):
        return (
            self.total_debits
            == self.total_credits
        )


# ============================================================
# JOURNAL ENTRY LINE
# ============================================================

class JournalEntryLine(TimeStampedModel):
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name="lines",
    )

    account = models.ForeignKey(
        LedgerAccount,
        on_delete=models.PROTECT,
        related_name="journal_lines",
    )

    debit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(Decimal("0"))
        ],
    )

    credit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(Decimal("0"))
        ],
    )

    description = models.CharField(
        max_length=255,
        blank=True,
    )

    class Meta:
        ordering = ["id"]

        indexes = [
            models.Index(
                fields=["journal_entry"]
            )
        ]

        constraints = [
            models.CheckConstraint(
                check=(
                    Q(debit__gt=0)
                    | Q(credit__gt=0)
                ),
                name="debit_or_credit_positive",
            ),
            models.CheckConstraint(
                check=(
                    Q(debit=0)
                    | Q(credit=0)
                ),
                name="journal_line_not_both_debit_credit",
            ),
        ]

    def __str__(self):
        return (
            f"{self.journal_entry.entry_number} - "
            f"{self.account.name}"
        )

    def clean(self):
        if (
            self.debit > 0
            and self.credit > 0
        ):
            raise ValidationError(
                "A journal entry line cannot "
                "have both debit and credit."
            )

        if (
            self.debit <= 0
            and self.credit <= 0
        ):
            raise ValidationError(
                "A journal entry line must have "
                "either a debit or credit amount."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# ============================================================
# PAYMENT DUE REMINDER
# ============================================================

class PaymentDueReminder(TimeStampedModel):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="reminders",
    )

    sent_at = models.DateTimeField(
        auto_now_add=True
    )

    channel = models.CharField(
        max_length=20,
        choices=[
            ("EMAIL", "Email"),
            ("SMS", "SMS"),
            ("PUSH", "Push"),
        ],
    )

    template = models.CharField(
        max_length=50,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        default="SENT",
        db_index=True,
    )

    error_message = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ["-sent_at"]

        indexes = [
            models.Index(
                fields=[
                    "invoice",
                    "sent_at",
                ]
            ),
            models.Index(fields=["status"]),
        ]

        verbose_name_plural = "Payment Reminders"

    def __str__(self):
        return (
            f"{self.invoice.invoice_number} - "
            f"{self.channel} at {self.sent_at}"
        )


# ============================================================
# CUSTOMER STATEMENT
# ============================================================

class CustomerStatement(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="statements",
    )

    statement_date = models.DateField(
        default=timezone.now,
        db_index=True,
    )

    opening_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    closing_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    pdf_file = models.FileField(
        upload_to="statements/pdfs/",
        blank=True,
        null=True,
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-statement_date"]

        indexes = [
            models.Index(
                fields=[
                    "customer",
                    "statement_date",
                ]
            )
        ]

        verbose_name_plural = "Customer Statements"

    def __str__(self):
        return (
            f"{self.customer.name} - "
            f"{self.statement_date}"
        )


# ============================================================
# CUSTOMER STATEMENT LINE
# ============================================================

class CustomerStatementLine(TimeStampedModel):
    statement = models.ForeignKey(
        CustomerStatement,
        on_delete=models.CASCADE,
        related_name="lines",
    )

    date = models.DateField(
        db_index=True
    )

    description = models.CharField(
        max_length=255
    )

    debit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    credit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    reference = models.CharField(
        max_length=50,
        blank=True,
    )

    class Meta:
        ordering = ["date"]

        indexes = [
            models.Index(
                fields=[
                    "statement",
                    "date",
                ]
            )
        ]

    def __str__(self):
        return (
            f"{self.date} - "
            f"{self.description}"
        )
