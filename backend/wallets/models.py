import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from common.models import TimeStampedModel


class Wallet(TimeStampedModel):
    """
    User wallet – holds balance and transaction history.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Current available balance"
    )

    total_earned = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total amount credited (all time)"
    )

    total_withdrawn = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total amount debited (all time)"
    )

    currency = models.CharField(
        max_length=10,
        default='GHS',
        help_text="Wallet currency (e.g., GHS, USD)"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether the wallet is active"
    )

    last_transaction_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the last transaction"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
        verbose_name_plural = "Wallets"

    def __str__(self):
        return f"{self.user.email} - {self.balance} {self.currency}"

    def credit(self, amount, description, reference=None, metadata=None):
        """
        Add funds to the wallet.
        """
        if amount <= 0:
            raise ValueError("Credit amount must be positive.")
        self.balance += amount
        self.total_earned += amount
        self.last_transaction_at = timezone.now()
        self.save()
        # Create transaction
        return WalletTransaction.objects.create(
            wallet=self,
            transaction_type=WalletTransaction.TransactionType.CREDIT,
            amount=amount,
            description=description,
            reference=reference or self.generate_transaction_ref(),
            balance_after=self.balance,
            metadata=metadata or {},
            status=WalletTransaction.TransactionStatus.COMPLETED,
            processed_at=timezone.now()
        )

    def debit(self, amount, description, reference=None, metadata=None):
        """
        Deduct funds from the wallet.
        """
        if amount <= 0:
            raise ValueError("Debit amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient balance.")
        self.balance -= amount
        self.total_withdrawn += amount
        self.last_transaction_at = timezone.now()
        self.save()
        return WalletTransaction.objects.create(
            wallet=self,
            transaction_type=WalletTransaction.TransactionType.DEBIT,
            amount=amount,
            description=description,
            reference=reference or self.generate_transaction_ref(),
            balance_after=self.balance,
            metadata=metadata or {},
            status=WalletTransaction.TransactionStatus.COMPLETED,
            processed_at=timezone.now()
        )

    def generate_transaction_ref(self):
        return f"WLT-{uuid.uuid4().hex[:12].upper()}"


class WalletTransaction(TimeStampedModel):
    """
    Individual transaction record for a wallet.
    """

    class TransactionType(models.TextChoices):
        CREDIT = 'CREDIT', 'Credit'
        DEBIT = 'DEBIT', 'Debit'

    class TransactionStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    description = models.TextField()

    reference = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )

    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Wallet balance after this transaction"
    )

    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the transaction was processed (if completed)"
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional data (e.g., related booking, payment ref)"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', 'transaction_type']),
            models.Index(fields=['reference']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
        verbose_name_plural = "Wallet Transactions"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Amount must be greater than zero.")
        if self.status == self.TransactionStatus.COMPLETED and not self.processed_at:
            raise ValidationError("Completed transactions must have a processed_at timestamp.")
        if self.status == self.TransactionStatus.PENDING and self.processed_at:
            raise ValidationError("Pending transactions cannot have a processed_at timestamp.")

    def complete(self):
        if self.status != self.TransactionStatus.PENDING:
            raise ValueError("Only pending transactions can be completed.")
        self.status = self.TransactionStatus.COMPLETED
        self.processed_at = timezone.now()
        self.save()

    def fail(self):
        if self.status != self.TransactionStatus.PENDING:
            raise ValueError("Only pending transactions can be failed.")
        self.status = self.TransactionStatus.FAILED
        self.save()

    def __str__(self):
        return f"{self.reference} - {self.transaction_type} {self.amount}"
