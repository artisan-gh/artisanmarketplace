import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from common.models import TimeStampedModel


class SubscriptionPlan(TimeStampedModel):
    """
    A subscription plan that users can subscribe to.
    """
    class BillingCycle(models.TextChoices):
        DAILY = 'DAILY', 'Daily'
        WEEKLY = 'WEEKLY', 'Weekly'
        MONTHLY = 'MONTHLY', 'Monthly'
        QUARTERLY = 'QUARTERLY', 'Quarterly'
        YEARLY = 'YEARLY', 'Yearly'

    name = models.CharField(
        max_length=100,
        help_text="Plan name (e.g., 'Pro Artisan')"
    )

    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per billing cycle"
    )

    currency = models.CharField(
        max_length=10,
        default='GHS'
    )

    billing_cycle = models.CharField(
        max_length=20,
        choices=BillingCycle.choices,
        default=BillingCycle.MONTHLY
    )

    duration_days = models.PositiveIntegerField(
        default=30,
        help_text="Duration in days (e.g., 30 for monthly)"
    )

    features = models.JSONField(
        default=list,
        blank=True,
        help_text="List of features included in this plan"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this plan is available for purchase"
    )

    # Optional: free trial
    trial_days = models.PositiveIntegerField(
        default=0,
        help_text="Number of free trial days (0 = no trial)"
    )

    # Optional: max users allowed
    max_users = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of users allowed under this plan"
    )

    # Optional: max listings/services
    max_listings = models.PositiveIntegerField(
        default=10,
        help_text="Maximum number of listings/services allowed"
    )

    # Optional: priority support
    priority_support = models.BooleanField(
        default=False,
        help_text="Whether this plan includes priority support"
    )

    class Meta:
        ordering = ['price']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['billing_cycle']),
        ]
        verbose_name_plural = "Subscription Plans"

    def __str__(self):
        return f"{self.name} - {self.price} {self.currency}"


class Subscription(TimeStampedModel):
    """
    A user's subscription to a plan.
    """
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        TRIAL = 'TRIAL', 'Trial'
        EXPIRED = 'EXPIRED', 'Expired'
        CANCELLED = 'CANCELLED', 'Cancelled'
        PAUSED = 'PAUSED', 'Paused'

    # ─── Relations ────────────────────────────────────────────
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    # ─── Dates ─────────────────────────────────────────────────
    start_date = models.DateField(
        help_text="Date when the subscription starts"
    )

    end_date = models.DateField(
        help_text="Date when the subscription ends (if not renewed)"
    )

    trial_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when the trial ends (if applicable)"
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the subscription was cancelled"
    )

    # ─── Status ──────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    auto_renew = models.BooleanField(
        default=True,
        help_text="Whether the subscription automatically renews"
    )

    # ─── Payment References ───────────────────────────────────
    subscription_reference = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Unique reference for this subscription"
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

    # ─── Metadata ─────────────────────────────────────────────
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['end_date']),
            models.Index(fields=['subscription_reference']),
        ]
        verbose_name_plural = "Subscriptions"

    def save(self, *args, **kwargs):
        if not self.subscription_reference:
            self.subscription_reference = self.generate_reference()
        self.full_clean()
        super().save(*args, **kwargs)

    def generate_reference(self):
        year = timezone.now().strftime('%Y')
        count = Subscription.objects.filter(created_at__year=timezone.now().year).count() + 1
        return f"SUB-{year}-{str(count).zfill(4)}"

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start date must be before end date.")
        if self.trial_end_date and self.trial_end_date > self.start_date:
            raise ValidationError("Trial end date must be before start date.")
        if self.start_date < timezone.now().date():
            # Allow if it's within the last day or so for backdating
            pass

    # ─── Properties ──────────────────────────────────────────

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    @property
    def is_expired(self):
        return self.status == self.Status.EXPIRED

    @property
    def days_remaining(self):
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return max(delta.days, 0)
        return 0

    @property
    def is_on_trial(self):
        if not self.trial_end_date:
            return False
        return timezone.now().date() <= self.trial_end_date

    # ─── Methods ──────────────────────────────────────────────

    def renew(self, duration_days=None, gateway_ref=None):
        """
        Renew the subscription for another billing cycle.
        """
        if self.status == self.Status.CANCELLED:
            raise ValueError("Cannot renew a cancelled subscription.")

        if not duration_days:
            duration_days = self.plan.duration_days

        self.start_date = timezone.now().date()
        self.end_date = self.start_date + timezone.timedelta(days=duration_days)
        self.status = self.Status.ACTIVE
        if gateway_ref:
            self.gateway_reference = gateway_ref
        self.save()
        return self

    def cancel(self, reason=""):
        """
        Cancel the subscription.
        """
        if self.status in [self.Status.CANCELLED, self.Status.EXPIRED]:
            raise ValueError("Subscription is already cancelled or expired.")

        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.auto_renew = False
        self.notes = reason
        self.save()
        return self

    def expire(self):
        """
        Mark the subscription as expired.
        """
        if self.status == self.Status.EXPIRED:
            raise ValueError("Subscription is already expired.")
        self.status = self.Status.EXPIRED
        self.save()
        return self

    def toggle_auto_renew(self):
        """
        Toggle auto-renewal.
        """
        self.auto_renew = not self.auto_renew
        self.save()
        return self

    def __str__(self):
        return f"{self.subscription_reference} - {self.user.email} - {self.plan.name}"
