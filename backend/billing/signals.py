# billing/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Invoice, InvoiceItem, InvoiceItemTax, PaymentAllocation, CreditNote,
    PurchasedItem
)


# ─── Recalculation signals ──────────────────────────────────────

def recalc_invoice(invoice):
    """Helper to recalc totals and update invoice record."""
    if not invoice or not invoice.pk:
        return
    invoice.calculate_totals()
    Invoice.objects.filter(pk=invoice.pk).update(
        subtotal=invoice.subtotal,
        tax_amount=invoice.tax_amount,
        materials_total=invoice.materials_total,
        grand_total=invoice.grand_total,
        balance_due=invoice.balance_due,
        converted_total=invoice.converted_total
    )


@receiver(post_save, sender=InvoiceItem)
def recalc_invoice_on_item_save(sender, instance, **kwargs):
    """Recalculate invoice totals when an item is saved."""
    if not instance.pk or not instance.invoice_id:
        return
    recalc_invoice(instance.invoice)


@receiver(post_delete, sender=InvoiceItem)
def recalc_invoice_on_item_delete(sender, instance, **kwargs):
    """Recalculate invoice totals when an item is deleted."""
    if not instance.pk or not instance.invoice_id:
        return
    recalc_invoice(instance.invoice)


@receiver(post_save, sender=InvoiceItemTax)
def recalc_item_and_invoice_on_tax_add(sender, instance, **kwargs):
    """Recalculate item totals when a tax is added/updated."""
    if not instance.pk or not instance.item_id:
        return
    item = instance.item
    item.calculate_totals()
    InvoiceItem.objects.filter(pk=item.pk).update(
        tax_rate=item.tax_rate,
        tax_amount=item.tax_amount,
        tax=item.tax,
        line_total=item.line_total
    )
    if item.invoice_id:
        recalc_invoice(item.invoice)


@receiver(post_delete, sender=InvoiceItemTax)
def recalc_item_and_invoice_on_tax_remove(sender, instance, **kwargs):
    """Recalculate item totals when a tax is removed."""
    if not instance.pk or not instance.item_id:
        return
    item = instance.item
    item.calculate_totals()
    InvoiceItem.objects.filter(pk=item.pk).update(
        tax_rate=item.tax_rate,
        tax_amount=item.tax_amount,
        tax=item.tax,
        line_total=item.line_total
    )
    if item.invoice_id:
        recalc_invoice(item.invoice)


# ─── Signals for PurchasedItem (materials) ─────────────────────

@receiver(post_save, sender=PurchasedItem)
def recalc_invoice_on_purchased_item_save(sender, instance, **kwargs):
    """Recalculate invoice totals when a purchased item is saved."""
    if not instance.pk or not instance.invoice_id:
        return
    recalc_invoice(instance.invoice)


@receiver(post_delete, sender=PurchasedItem)
def recalc_invoice_on_purchased_item_delete(sender, instance, **kwargs):
    """Recalculate invoice totals when a purchased item is deleted."""
    if not instance.pk or not instance.invoice_id:
        return
    recalc_invoice(instance.invoice)


# ─── Payment Allocation signals ─────────────────────────────────

@receiver(post_save, sender=PaymentAllocation)
def update_invoice_on_allocation_save(sender, instance, **kwargs):
    """Update invoice paid amount when allocation is saved."""
    if not instance.pk or not instance.invoice_id:
        return
    instance.invoice.update_paid_amount()


@receiver(post_delete, sender=PaymentAllocation)
def update_invoice_on_allocation_delete(sender, instance, **kwargs):
    """Update invoice paid amount when allocation is deleted."""
    if not instance.pk or not instance.invoice_id:
        return
    instance.invoice.update_paid_amount()


# ─── Credit Note signals ────────────────────────────────────────

@receiver(post_save, sender=CreditNote)
def update_invoice_on_credit_note_save(sender, instance, **kwargs):
    """Recalculate invoice totals when a credit note is saved."""
    if not instance.pk or not instance.invoice_id:
        return
    recalc_invoice(instance.invoice)


@receiver(post_delete, sender=CreditNote)
def update_invoice_on_credit_note_delete(sender, instance, **kwargs):
    """Recalculate invoice totals when a credit note is deleted."""
    if not instance.pk or not instance.invoice_id:
        return
    recalc_invoice(instance.invoice)


# ─── Invoice Paid Notification ────────────────────────────────

@receiver(post_save, sender=Invoice)
def invoice_paid_notification(sender, instance, **kwargs):
    """
    Send a confirmation email when invoice status changes to PAID.
    """
    # Skip if it's a new invoice
    if kwargs.get('created', False):
        return

    # Check if status changed to PAID (requires FieldTracker on Invoice)
    if hasattr(instance, 'tracker') and instance.tracker.has_changed('status') and instance.status == 'PAID':
        customer = instance.customer
        if not customer:
            return

        recipient_email = None
        if hasattr(customer, 'user') and customer.user:
            recipient_email = customer.user.email
        elif hasattr(customer, 'email') and customer.email:
            recipient_email = customer.email

        if not recipient_email:
            return

        subject = f"Invoice #{instance.invoice_number} Paid – ArtisanHub"
        message = f"""
Dear Customer,

Your invoice {instance.invoice_number} of ₵{instance.grand_total} has been fully paid.

Thank you for your payment!

ArtisanHub Team
        """

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            print(f"Payment confirmation email sent to {recipient_email}")
        except Exception as e:
            print(f"Failed to send payment confirmation email: {e}")


# ─── NOTE: invoice_created_notification has been removed ──────
# Invoice creation emails are now sent directly from the serializer's
# create() method in billing/serializers.py (InvoiceCreateUpdateSerializer).
# This ensures the email is sent ONLY after all items and totals are saved.