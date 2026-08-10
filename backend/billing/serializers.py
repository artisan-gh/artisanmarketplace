# billing/serializers.py

from decimal import Decimal

from django.db import transaction

from rest_framework import serializers

from .models import (
    Invoice,
    InvoiceItem,
    InvoiceItemTax,
    BillingConfig,
    Payment,
    PaymentAllocation,
    CreditNote,
    InvoiceApproval,
    InvoiceHistory,
    InvoiceTag,
    InvoiceComment,
    InvoiceAttachment,
    RecurringInvoice,
    LedgerAccount,
    JournalEntry,
    JournalEntryLine,
    PaymentIntent,
    PaymentGatewayTransaction,
    WebhookLog,
    PaymentDueReminder,
    CustomerStatement,
    CustomerStatementLine,
    InvoiceStatus,
    Tax,
    PurchasedItem,
)

from customers.serializers import CustomerListSerializer
from accounts.serializers import UserListSerializer


# ============================================================
# HELPERS
# ============================================================

def get_user_full_name(user):
    """Safely return a user's full name."""
    if not user:
        return None

    try:
        name = user.get_full_name()
        return name or getattr(user, "email", None)
    except AttributeError:
        return getattr(user, "email", None)


def attach_taxes_to_item(item, tax_ids):
    """
    Attach Tax records to an InvoiceItem through InvoiceItemTax.
    The first tax becomes the primary tax on InvoiceItem.tax.
    Invalid UUIDs / missing taxes are ignored.
    """
    if not tax_ids:
        return

    primary_tax = None

    for tax_id in tax_ids:
        try:
            tax = Tax.objects.get(pk=tax_id)

            InvoiceItemTax.objects.create(
                item=item,
                tax=tax,
            )

            if primary_tax is None:
                primary_tax = tax

        except Tax.DoesNotExist:
            continue

    if primary_tax:
        item.tax = primary_tax


def create_invoice_item(invoice, item_data):
    """
    Create an InvoiceItem and calculate its totals.
    """
    tax_ids = item_data.pop("taxes", [])

    item = InvoiceItem.objects.create(
        invoice=invoice,
        **item_data,
    )

    attach_taxes_to_item(item, tax_ids)

    item.calculate_totals()

    item.save()

    return item


def replace_invoice_items(invoice, items_data):
    """
    Replace all invoice items with a new collection.
    """
    invoice.items.all().delete()

    for item_data in items_data:
        create_invoice_item(invoice, item_data)


def replace_purchased_items(invoice, purchased_items_data):
    """
    Replace all purchased/material items for an invoice.
    """
    invoice.purchased_items.all().delete()

    for item_data in purchased_items_data:
        PurchasedItem.objects.create(
            invoice=invoice,
            **item_data,
        )


def replace_invoice_tags(invoice, tags_data):
    """
    Replace invoice tags using tag names.
    """
    invoice.tags.clear()

    for tag_name in tags_data:
        if not tag_name:
            continue

        tag_name = str(tag_name).strip()

        if not tag_name:
            continue

        tag, _ = InvoiceTag.objects.get_or_create(
            name=tag_name
        )

        invoice.tags.add(tag)


# ============================================================
# TAX
# ============================================================

class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# ============================================================
# PAYMENT ALLOCATIONS
# ============================================================

class PaymentAllocationSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(
        source="invoice.invoice_number",
        read_only=True,
    )

    invoice_grand_total = serializers.DecimalField(
        source="invoice.grand_total",
        max_digits=12,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False,
    )

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = PaymentAllocation
        fields = [
            "id",
            "invoice",
            "invoice_number",
            "invoice_grand_total",
            "amount",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]

    def validate_amount(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError(
                "Allocation amount must be greater than zero."
            )

        return value


class PaymentAllocationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAllocation
        fields = [
            "invoice",
            "amount",
        ]

    def validate_amount(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError(
                "Allocation amount must be greater than zero."
            )

        return value


# ============================================================
# PAYMENTS
# ============================================================

class PaymentListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.name",
        read_only=True,
    )

    allocations_count = serializers.IntegerField(
        source="allocations.count",
        read_only=True,
    )

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "customer",
            "customer_name",
            "amount",
            "currency",
            "method",
            "status",
            "gateway_reference",
            "paid_at",
            "allocations_count",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    allocations = PaymentAllocationSerializer(
        many=True,
        read_only=True,
    )

    customer_detail = serializers.SerializerMethodField()

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = Payment
        fields = "__all__"

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def get_customer_detail(self, obj):
        if not obj.customer:
            return None

        return CustomerListSerializer(
            obj.customer
        ).data


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment

        fields = [
            "customer",
            "amount",
            "currency",
            "method",
            "gateway",
            "description",
            "metadata",
        ]

    def validate_amount(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError(
                "Payment amount must be greater than zero."
            )

        return value


class RefundSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
        coerce_to_string=False,
        help_text="Leave blank for a full refund.",
    )

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def validate_amount(self, value):
        if value is not None and value <= Decimal("0.00"):
            raise serializers.ValidationError(
                "Refund amount must be greater than zero."
            )

        return value


# ============================================================
# INVOICE ITEM TAX
# ============================================================

class InvoiceItemTaxSerializer(serializers.ModelSerializer):
    tax_name = serializers.CharField(
        source="tax.name",
        read_only=True,
    )

    tax_rate = serializers.DecimalField(
        source="tax.rate",
        max_digits=5,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False,
    )

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = InvoiceItemTax

        fields = [
            "id",
            "tax",
            "tax_name",
            "tax_rate",
            "rate_override",
            "amount",
        ]

        read_only_fields = [
            "id",
            "amount",
        ]


# ============================================================
# PURCHASED ITEMS / MATERIALS
# ============================================================

class PurchasedItemSerializer(serializers.ModelSerializer):
    total_cost = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False,
    )

    class Meta:
        model = PurchasedItem

        fields = [
            "id",
            "description",
            "quantity",
            "unit_cost",
            "total_cost",
        ]

        read_only_fields = [
            "id",
            "total_cost",
        ]

    def validate_quantity(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError(
                "Quantity must be greater than zero."
            )

        return value

    def validate_unit_cost(self, value):
        if value < Decimal("0.00"):
            raise serializers.ValidationError(
                "Unit cost cannot be negative."
            )

        return value


# ============================================================
# INVOICE ITEMS
# ============================================================

class InvoiceItemSerializer(serializers.ModelSerializer):
    quantity = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False,
    )

    unit_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    discount_percent = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False,
    )

    discount_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    tax_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False,
    )

    tax_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    line_subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    line_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    item_taxes = InvoiceItemTaxSerializer(
        many=True,
        read_only=True,
    )

    tax_detail = TaxSerializer(
        source="tax",
        read_only=True,
    )

    class Meta:
        model = InvoiceItem

        fields = [
            "id",
            "invoice",
            "description",
            "sku",
            "unit",
            "quantity",
            "unit_price",
            "discount_percent",
            "discount_amount",
            "tax",
            "tax_detail",
            "tax_rate",
            "tax_amount",
            "line_subtotal",
            "line_total",
            "item_taxes",
            "incident",
            "assignment",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "tax_rate",
            "tax_amount",
            "line_subtotal",
            "line_total",
            "created_at",
            "updated_at",
        ]


class InvoiceItemCreateSerializer(serializers.ModelSerializer):
    taxes = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        write_only=True,
        allow_empty=True,
        help_text="List of Tax UUIDs to attach to this item.",
    )

    # These are accepted when the frontend explicitly provides
    # manual tax information.
    tax_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        default=Decimal("0.00"),
        coerce_to_string=False,
    )

    tax_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        default=Decimal("0.00"),
        coerce_to_string=False,
    )

    class Meta:
        model = InvoiceItem

        fields = [
            "description",
            "sku",
            "unit",
            "quantity",
            "unit_price",
            "discount_percent",
            "discount_amount",
            "incident",
            "assignment",
            "tax_rate",
            "tax_amount",
            "taxes",
        ]

    def validate_quantity(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError(
                "Quantity must be greater than zero."
            )

        return value

    def validate_unit_price(self, value):
        if value < Decimal("0.00"):
            raise serializers.ValidationError(
                "Unit price cannot be negative."
            )

        return value

    def validate_discount_percent(self, value):
        if value < Decimal("0.00") or value > Decimal("100.00"):
            raise serializers.ValidationError(
                "Discount percentage must be between 0 and 100."
            )

        return value

    def validate_discount_amount(self, value):
        if value < Decimal("0.00"):
            raise serializers.ValidationError(
                "Discount amount cannot be negative."
            )

        return value

    def validate_tax_rate(self, value):
        if value < Decimal("0.00"):
            raise serializers.ValidationError(
                "Tax rate cannot be negative."
            )

        return value

    def validate_tax_amount(self, value):
        if value < Decimal("0.00"):
            raise serializers.ValidationError(
                "Tax amount cannot be negative."
            )

        return value

    def create(self, validated_data):
        taxes = validated_data.pop("taxes", [])

        item = InvoiceItem.objects.create(
            **validated_data
        )

        attach_taxes_to_item(
            item,
            taxes,
        )

        item.calculate_totals()
        item.save()

        return item

    def update(self, instance, validated_data):
        taxes = validated_data.pop(
            "taxes",
            None,
        )

        for attr, value in validated_data.items():
            setattr(
                instance,
                attr,
                value,
            )

        if taxes is not None:
            instance.item_taxes.all().delete()

            instance.tax = None

            attach_taxes_to_item(
                instance,
                taxes,
            )

        instance.calculate_totals()
        instance.save()

        return instance


# ============================================================
# INVOICE LIST
# ============================================================

class InvoiceListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.name",
        read_only=True,
    )

    customer_phone = serializers.CharField(
        source="customer.phone",
        read_only=True,
    )

    balance_due = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False,
    )

    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    tax_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    discount_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    grand_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    amount_paid = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    transport_cost = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False,
    )

    aging_category = serializers.SerializerMethodField()

    class Meta:
        model = Invoice

        fields = [
            "id",
            "invoice_number",
            "public_token",
            "customer",
            "customer_name",
            "customer_phone",
            "subtotal",
            "tax_amount",
            "discount_amount",
            "grand_total",
            "amount_paid",
            "balance_due",
            "currency",
            "status",
            "invoice_type",
            "issued_date",
            "due_date",
            "is_overdue",
            "is_paid",
            "aging_category",
            "transport_cost",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "invoice_number",
            "public_token",
            "subtotal",
            "tax_amount",
            "grand_total",
            "amount_paid",
            "balance_due",
            "is_overdue",
            "is_paid",
            "aging_category",
            "transport_cost",
            "created_at",
        ]

    def get_aging_category(self, obj):
        try:
            return obj.get_aging_category()
        except AttributeError:
            return None


# ============================================================
# INVOICE DETAIL
# ============================================================

class InvoiceDetailSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(
        many=True,
        read_only=True,
    )

    customer_detail = CustomerListSerializer(
        source="customer",
        read_only=True,
        default=None,
    )

    created_by_detail = UserListSerializer(
        source="created_by",
        read_only=True,
        default=None,
    )

    email_sent_by_detail = UserListSerializer(
        source="email_sent_by",
        read_only=True,
        default=None,
    )

    status_name = serializers.CharField(
        source="status",
        read_only=True,
    )

    created_by_name = serializers.SerializerMethodField()

    customer_name = serializers.SerializerMethodField()

    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    tax_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    discount_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    grand_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    amount_paid = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    balance_due = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    materials_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    transport_cost = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False,
    )

    purchased_items = PurchasedItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Invoice

        fields = [
            "id",
            "invoice_number",
            "public_token",
            "customer",
            "customer_detail",
            "customer_name",
            "created_by",
            "created_by_detail",
            "created_by_name",
            "email_sent_by",
            "email_sent_by_detail",
            "invoice_type",
            "status",
            "status_name",
            "billing_name",
            "billing_address",
            "billing_phone",
            "billing_email",
            "billing_tax_id",
            "billing_organization",
            "issued_date",
            "due_date",
            "paid_date",
            "subtotal",
            "tax_amount",
            "discount_amount",
            "grand_total",
            "amount_paid",
            "balance_due",
            "currency",
            "notes",
            "terms",
            "items",
            "is_overdue",
            "is_paid",
            "is_fully_paid",
            "created_at",
            "updated_at",
            "materials_total",
            "transport_cost",
            "purchased_items",
        ]

        read_only_fields = [
            "id",
            "invoice_number",
            "public_token",
            "subtotal",
            "tax_amount",
            "grand_total",
            "amount_paid",
            "balance_due",
            "is_overdue",
            "is_paid",
            "is_fully_paid",
            "created_at",
            "updated_at",
            "materials_total",
            "transport_cost",
        ]

    def get_created_by_name(self, obj):
        return get_user_full_name(
            obj.created_by
        )

    def get_customer_name(self, obj):
        if not obj.customer:
            return None

        return getattr(
            obj.customer,
            "name",
            None,
        )


# ============================================================
# INVOICE CREATE / UPDATE
# ============================================================

class InvoiceCreateUpdateSerializer(serializers.ModelSerializer):
    items = InvoiceItemCreateSerializer(
        many=True,
        required=False,
    )

    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True,
        allow_empty=True,
        help_text="List of tag names to attach to the invoice.",
    )

    purchased_items = PurchasedItemSerializer(
        many=True,
        required=False,
    )

    transport_cost = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        default=Decimal("0.00"),
        coerce_to_string=False,
        help_text="Cost of transportation/delivery for this invoice.",
    )

    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False,
    )

    tax_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False,
    )

    grand_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False,
    )

    materials_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False,
    )

    discount_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        default=Decimal("0.00"),
        coerce_to_string=False,
    )

    class Meta:
        model = Invoice

        fields = [
            "customer",
            "incident",
            "organization",
            "branch",
            "department",
            "invoice_type",
            "billing_name",
            "billing_address",
            "billing_phone",
            "billing_email",
            "billing_tax_id",
            "billing_organization",
            "issued_date",
            "due_date",
            "discount_amount",
            "currency",
            "notes",
            "terms",
            "items",
            "tags",
            "purchased_items",
            "transport_cost",
            "subtotal",
            "tax_amount",
            "grand_total",
            "materials_total",
        ]

    def validate_transport_cost(self, value):
        if value < Decimal("0.00"):
            raise serializers.ValidationError(
                "Transport cost cannot be negative."
            )
        return value

    def validate_discount_amount(self, value):
        if value < Decimal("0.00"):
            raise serializers.ValidationError(
                "Discount amount cannot be negative."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):

        items_data = validated_data.pop(
            "items",
            [],
        )

        tags_data = validated_data.pop(
            "tags",
            [],
        )

        purchased_items_data = validated_data.pop(
            "purchased_items",
            [],
        )

        invoice = Invoice.objects.create(
            **validated_data
        )

        # ----------------------------------------------------
        # Invoice items
        # ----------------------------------------------------

        for item_data in items_data:
            create_invoice_item(
                invoice,
                item_data,
            )

        # ----------------------------------------------------
        # Purchased / material items
        # ----------------------------------------------------

        for pitem_data in purchased_items_data:
            PurchasedItem.objects.create(
                invoice=invoice,
                **pitem_data,
            )

        # ----------------------------------------------------
        # Tags
        # ----------------------------------------------------

        replace_invoice_tags(
            invoice,
            tags_data,
        )

        # ----------------------------------------------------
        # Calculate invoice totals
        # ----------------------------------------------------

        invoice.calculate_totals()
        invoice.save()

        # ----------------------------------------------------
        # Send invoice email
        # ----------------------------------------------------

        self._send_invoice_email(invoice)

        return invoice

    @transaction.atomic
    def update(self, instance, validated_data):

        items_data = validated_data.pop(
            "items",
            None,
        )

        tags_data = validated_data.pop(
            "tags",
            None,
        )

        purchased_items_data = validated_data.pop(
            "purchased_items",
            None,
        )

        # ----------------------------------------------------
        # Update normal fields
        # ----------------------------------------------------

        for attr, value in validated_data.items():
            setattr(
                instance,
                attr,
                value,
            )

        instance.save()

        # ----------------------------------------------------
        # Replace invoice items if supplied
        # ----------------------------------------------------

        if items_data is not None:
            replace_invoice_items(
                instance,
                items_data,
            )

        # ----------------------------------------------------
        # Replace purchased items if supplied
        # ----------------------------------------------------

        if purchased_items_data is not None:
            replace_purchased_items(
                instance,
                purchased_items_data,
            )

        # ----------------------------------------------------
        # Replace tags if supplied
        # ----------------------------------------------------

        if tags_data is not None:
            replace_invoice_tags(
                instance,
                tags_data,
            )

        # ----------------------------------------------------
        # Recalculate totals
        # ----------------------------------------------------

        instance.calculate_totals()
        instance.save()

        return instance

    def _send_invoice_email(self, invoice):

        if not invoice.customer:
            return

        recipient_email = None

        customer = invoice.customer

        if hasattr(customer, "user") and customer.user:
            recipient_email = getattr(
                customer.user,
                "email",
                None,
            )

        if not recipient_email:
            recipient_email = getattr(
                customer,
                "email",
                None,
            )

        if not recipient_email:
            return

        if invoice.grand_total <= Decimal("0.00"):
            return

        try:
            from .utils import send_invoice_email

            send_invoice_email(
                invoice,
                recipient_email,
            )

        except Exception:
            # Email failure should not break invoice creation.
            pass


# ============================================================
# INVOICE STATUS TRANSITION
# ============================================================

class InvoiceStatusTransitionSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(
        choices=InvoiceStatus.choices,
    )

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
    )


# ============================================================
# INVOICE COMMENTS
# ============================================================

class InvoiceCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.get_full_name",
        read_only=True,
    )

    class Meta:
        model = InvoiceComment

        fields = [
            "id",
            "user",
            "user_name",
            "text",
            "is_internal",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "created_at",
        ]

    def create(self, validated_data):

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authenticated user is required."
            )

        validated_data["user"] = request.user

        return super().create(
            validated_data
        )


# ============================================================
# INVOICE ATTACHMENTS
# ============================================================

class InvoiceAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(
        source="uploaded_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = InvoiceAttachment

        fields = [
            "id",
            "file",
            "filename",
            "description",
            "uploaded_by",
            "uploaded_by_name",
            "file_size",
            "mime_type",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "uploaded_by",
            "created_at",
        ]

    def create(self, validated_data):

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authenticated user is required."
            )

        validated_data["uploaded_by"] = request.user

        return super().create(
            validated_data
        )


# ============================================================
# INVOICE APPROVAL
# ============================================================

class InvoiceApprovalSerializer(serializers.ModelSerializer):
    approver_name = serializers.CharField(
        source="approver.get_full_name",
        read_only=True,
    )

    class Meta:
        model = InvoiceApproval

        fields = [
            "id",
            "level",
            "approver",
            "approver_name",
            "status",
            "comments",
            "approved_at",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


class InvoiceApprovalActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=[
            ("approve", "Approve"),
            ("reject", "Reject"),
        ]
    )

    comments = serializers.CharField(
        required=False,
        allow_blank=True,
    )


# ============================================================
# INVOICE TAGS
# ============================================================

class InvoiceTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceTag

        fields = [
            "id",
            "name",
            "color",
        ]

        read_only_fields = [
            "id",
        ]


# ============================================================
# CREDIT NOTES
# ============================================================

class CreditNoteListSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(
        source="invoice.invoice_number",
        read_only=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.get_full_name",
        read_only=True,
    )

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = CreditNote

        fields = [
            "id",
            "credit_number",
            "invoice",
            "invoice_number",
            "amount",
            "currency",
            "status",
            "reason",
            "created_by",
            "created_by_name",
            "issued_date",
            "expiry_date",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "credit_number",
            "created_at",
        ]


class CreditNoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditNote

        fields = [
            "invoice",
            "payment",
            "amount",
            "reason",
            "currency",
            "expiry_date",
        ]

    def validate_amount(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError(
                "Credit note amount must be greater than zero."
            )

        return value


# ============================================================
# INVOICE HISTORY
# ============================================================

class InvoiceHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.get_full_name",
        read_only=True,
    )

    class Meta:
        model = InvoiceHistory

        fields = [
            "id",
            "action",
            "user",
            "user_name",
            "reason",
            "old_status",
            "new_status",
            "metadata",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


# ============================================================
# RECURRING INVOICE
# ============================================================

class RecurringInvoiceListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.name",
        read_only=True,
    )

    class Meta:
        model = RecurringInvoice

        fields = [
            "id",
            "customer",
            "customer_name",
            "frequency",
            "next_issue_date",
            "is_active",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


class RecurringInvoiceDetailSerializer(serializers.ModelSerializer):
    customer_detail = CustomerListSerializer(
        source="customer",
        read_only=True,
    )

    class Meta:
        model = RecurringInvoice

        fields = "__all__"

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# ============================================================
# LEDGER ACCOUNTS
# ============================================================

class LedgerAccountListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerAccount

        fields = [
            "id",
            "code",
            "name",
            "account_type",
            "is_active",
        ]

        read_only_fields = [
            "id",
        ]


class LedgerAccountDetailSerializer(serializers.ModelSerializer):
    children = LedgerAccountListSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = LedgerAccount

        fields = "__all__"

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# ============================================================
# JOURNAL ENTRIES
# ============================================================

class JournalEntryLineSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(
        source="account.name",
        read_only=True,
    )

    account_code = serializers.CharField(
        source="account.code",
        read_only=True,
    )

    debit = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    credit = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = JournalEntryLine

        fields = [
            "id",
            "account",
            "account_name",
            "account_code",
            "debit",
            "credit",
            "description",
        ]

        read_only_fields = [
            "id",
        ]


class JournalEntryListSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(
        source="invoice.invoice_number",
        read_only=True,
    )

    class Meta:
        model = JournalEntry

        fields = [
            "id",
            "entry_number",
            "description",
            "invoice_number",
            "posted_at",
        ]

        read_only_fields = [
            "id",
            "posted_at",
        ]


class JournalEntryDetailSerializer(serializers.ModelSerializer):
    lines = JournalEntryLineSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = JournalEntry

        fields = "__all__"

        read_only_fields = [
            "id",
            "posted_at",
        ]


# ============================================================
# PAYMENT INTENTS
# ============================================================

class PaymentIntentListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.name",
        read_only=True,
    )

    invoice_number = serializers.CharField(
        source="invoice.invoice_number",
        read_only=True,
    )

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = PaymentIntent

        fields = [
            "id",
            "customer",
            "customer_name",
            "invoice",
            "invoice_number",
            "amount",
            "currency",
            "gateway",
            "gateway_reference",
            "status",
            "expires_at",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


# ============================================================
# PAYMENT GATEWAY TRANSACTIONS
# ============================================================

class PaymentGatewayTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGatewayTransaction

        fields = "__all__"

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# ============================================================
# WEBHOOK LOG
# ============================================================

class WebhookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookLog

        fields = "__all__"

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# ============================================================
# PAYMENT DUE REMINDERS
# ============================================================

class PaymentDueReminderSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(
        source="invoice.invoice_number",
        read_only=True,
    )

    class Meta:
        model = PaymentDueReminder

        fields = [
            "id",
            "invoice",
            "invoice_number",
            "channel",
            "status",
            "error_message",
            "sent_at",
        ]

        read_only_fields = [
            "id",
            "sent_at",
        ]


# ============================================================
# CUSTOMER STATEMENTS
# ============================================================

class CustomerStatementLineSerializer(serializers.ModelSerializer):
    debit = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    credit = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    balance = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = CustomerStatementLine

        fields = [
            "id",
            "date",
            "description",
            "debit",
            "credit",
            "balance",
            "reference",
        ]

        read_only_fields = [
            "id",
        ]


class CustomerStatementListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.name",
        read_only=True,
    )

    opening_balance = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    closing_balance = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = CustomerStatement

        fields = [
            "id",
            "customer",
            "customer_name",
            "statement_date",
            "opening_balance",
            "closing_balance",
        ]

        read_only_fields = [
            "id",
        ]


class CustomerStatementDetailSerializer(serializers.ModelSerializer):
    lines = CustomerStatementLineSerializer(
        many=True,
        read_only=True,
    )

    customer_detail = CustomerListSerializer(
        source="customer",
        read_only=True,
    )

    opening_balance = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    closing_balance = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = CustomerStatement

        fields = "__all__"

        read_only_fields = [
            "id",
        ]


# ============================================================
# BILLING CONFIGURATION
# ============================================================

class BillingConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingConfig

        fields = "__all__"

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# ============================================================
# PAYSTACK
# ============================================================

class PaystackInitializeSerializer(serializers.Serializer):
    invoice_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )

    callback_url = serializers.URLField(
        required=False,
        allow_blank=True,
    )


class PaystackWebhookSerializer(serializers.Serializer):
    event = serializers.CharField()

    data = serializers.JSONField()