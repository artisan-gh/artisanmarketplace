from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from common.models import TimeStampedModel


class VerificationDocumentType(models.Model):
    """
    Types of verification documents.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    required_for_artisan = models.BooleanField(default=False)
    required_for_client = models.BooleanField(default=False)
    required_for_company = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        verbose_name = "Document Type"
        verbose_name_plural = "Document Types"

    def __str__(self):
        return self.name


class VerificationRequest(TimeStampedModel):
    """
    A user's verification request with document upload.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        REVIEWING = 'REVIEWING', 'Reviewing'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        EXPIRED = 'EXPIRED', 'Expired'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class DocumentType(models.TextChoices):
        NATIONAL_ID = 'NATIONAL_ID', 'National ID'
        PASSPORT = 'PASSPORT', 'Passport'
        DRIVERS_LICENSE = 'DRIVERS_LICENSE', "Driver's License"
        UTILITY_BILL = 'UTILITY_BILL', 'Utility Bill'
        BUSINESS_REG = 'BUSINESS_REG', 'Business Registration'
        PROOF_OF_ADDRESS = 'PROOF_OF_ADDRESS', 'Proof of Address'
        OTHER = 'OTHER', 'Other'

    # ─── Relations ────────────────────────────────────────────
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='verification_requests'
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verifications_reviewed'
    )

    document_type = models.ForeignKey(
        VerificationDocumentType,
        on_delete=models.PROTECT,
        null=True,          # add
        blank=True,         # add
        related_name='verification_requests'
    )

    # ─── Document ─────────────────────────────────────────────
    document = models.FileField(
        upload_to='verification/%Y/%m/%d/',
        help_text="Upload your verification document (PDF, JPG, PNG)"
    )

    document_back = models.FileField(
        upload_to='verification/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Back side of document (if applicable)"
    )

    document_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Document number or ID"
    )

    # ─── Status ──────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # ─── Notes & Feedback ─────────────────────────────────────
    notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    # ─── Metadata ─────────────────────────────────────────────
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
        verbose_name_plural = "Verification Requests"

    def __str__(self):
        return f"{self.user.email} - {self.document_type.name} ({self.status})"

    def clean(self):
        if self.document and not self.document.name.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            raise ValidationError("Document must be PDF, JPG, JPEG, or PNG.")

    # ─── Status transitions ──────────────────────────────────

    def approve(self, reviewed_by=None):
        if self.status not in [self.Status.PENDING, self.Status.REVIEWING]:
            raise ValueError("Only pending or reviewing requests can be approved.")
        self.status = self.Status.APPROVED
        self.approved_at = timezone.now()
        self.reviewed_at = timezone.now()
        if reviewed_by:
            self.reviewed_by = reviewed_by
        self.save()

    def reject(self, reason="", reviewed_by=None):
        if self.status not in [self.Status.PENDING, self.Status.REVIEWING]:
            raise ValueError("Only pending or reviewing requests can be rejected.")
        self.status = self.Status.REJECTED
        self.rejected_at = timezone.now()
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason
        if reviewed_by:
            self.reviewed_by = reviewed_by
        self.save()

    def start_review(self):
        if self.status != self.Status.PENDING:
            raise ValueError("Only pending requests can be moved to reviewing.")
        self.status = self.Status.REVIEWING
        self.save()

    def cancel(self):
        if self.status in [self.Status.APPROVED, self.Status.REJECTED]:
            raise ValueError("Cannot cancel approved or rejected requests.")
        self.status = self.Status.CANCELLED
        self.save()

    def expire(self):
        if self.status in [self.Status.APPROVED, self.Status.REJECTED]:
            raise ValueError("Cannot expire approved or rejected requests.")
        self.status = self.Status.EXPIRED
        self.save()

    @property
    def is_pending(self):
        return self.status == self.Status.PENDING

    @property
    def is_approved(self):
        return self.status == self.Status.APPROVED

    @property
    def is_rejected(self):
        return self.status == self.Status.REJECTED
