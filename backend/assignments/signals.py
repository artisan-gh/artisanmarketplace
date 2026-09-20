"""
Auto-credit the artisan's wallet when an assignment is completed.

Fires on `Assignment.status` transition from IN_PROGRESS to COMPLETED.
Amount = invoice.grand_total minus platform fee.

Field assumptions (adjust if yours differ):
    Assignment.artisan      → FK to User
    Assignment.incident     → FK to Incident
    Invoice.incident        → FK to Incident
"""
from decimal import Decimal

from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Assignment


PLATFORM_FEE_PCT = Decimal('0.10')  # 10%


@receiver(pre_save, sender=Assignment)
def _stash_old_status(sender, instance, **kwargs):
    """Remember the previous status so post_save can detect the transition."""
    if not instance.pk:
        instance._old_status = None
        return
    instance._old_status = (
        Assignment.objects.filter(pk=instance.pk)
        .values_list('status', flat=True)
        .first()
    )


@receiver(post_save, sender=Assignment)
def _on_assignment_status_change(sender, instance, created, **kwargs):
    if created:
        return

    old = getattr(instance, '_old_status', None)
    if old == instance.status:
        return
    if instance.status != 'COMPLETED':
        return

    # Only credit the artisan the first time it flips to COMPLETED
    if old not in ('IN_PROGRESS', 'ACCEPTED', 'PENDING'):
        return

    _credit_artisan_for_completed_assignment(instance)


@transaction.atomic
def _credit_artisan_for_completed_assignment(assignment):
    from wallets.models import Wallet, WalletTransaction
    from billing.models import Invoice

    artisan = getattr(assignment, 'artisan', None)
    if not artisan:
        print(f"[payout] assignment {assignment.id} has no artisan")
        return

    # Find the invoice for this incident (latest one)
    invoice = (
        Invoice.objects
        .filter(incident=assignment.incident)
        .order_by('-created_at')
        .first()
    )
    if not invoice:
        print(f"[payout] no invoice found for incident {assignment.incident_id}")
        return

    total = invoice.grand_total or Decimal('0')
    if total <= 0:
        print(f"[payout] invoice {invoice.invoice_number} has zero total")
        return

    # Idempotency — don't credit twice for the same invoice
    already = WalletTransaction.objects.filter(
        reference=f'ESC-{invoice.invoice_number}',
    ).exists()
    if already:
        print(f"[payout] {invoice.invoice_number} already credited, skipping")
        return

    fee = (total * PLATFORM_FEE_PCT).quantize(Decimal('0.01'))
    artisan_share = total - fee

    wallet, _ = Wallet.objects.get_or_create(
        user=artisan,
        defaults={
            'balance': Decimal('0.00'),
            'currency': 'GHS',
            'total_earned': Decimal('0.00'),
            'total_withdrawn': Decimal('0.00'),
        },
    )

    wallet.balance += artisan_share
    wallet.total_earned += artisan_share
    wallet.last_transaction_at = timezone.now()
    wallet.save()

    WalletTransaction.objects.create(
        wallet=wallet,
        transaction_type=WalletTransaction.TransactionType.CREDIT,
        amount=artisan_share,
        description=f'Escrow release for {invoice.invoice_number}',
        reference=f'ESC-{invoice.invoice_number}',
        balance_after=wallet.balance,
        status=WalletTransaction.TransactionStatus.COMPLETED,
        processed_at=timezone.now(),
    )

    print(
        f"[payout] credited {artisan_share} to {artisan.email} "
        f"from {invoice.invoice_number} (fee {fee})"
    )