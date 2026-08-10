import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from common.models import TimeStampedModel


class AIModel(TimeStampedModel):
    """
    AI model metadata – tracks which AI models are available.
    """
    PROVIDER_CHOICES = (
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('cohere', 'Cohere'),
        ('google', 'Google AI'),
        ('local', 'Local Model'),
        ('custom', 'Custom'),
    )

    MODEL_TYPES = (
        ('chat', 'Chat / Conversation'),
        ('embedding', 'Embedding'),
        ('classification', 'Classification'),
        ('recommendation', 'Recommendation'),
        ('matching', 'Matching'),
        ('translation', 'Translation'),
        ('generation', 'Generation'),
    )

    name = models.CharField(max_length=100, db_index=True)
    version = models.CharField(max_length=50, db_index=True)
    description = models.TextField(blank=True)

    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default='openai')
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES, default='chat')
    model_id = models.CharField(max_length=100, help_text="Provider's model ID (e.g., gpt-4, claude-3)")

    # Configuration
    config = models.JSONField(default=dict, blank=True, help_text="Model-specific configuration (temperature, top_p, etc.)")
    max_tokens = models.PositiveIntegerField(default=4096)
    cost_per_1k_tokens = models.DecimalField(max_digits=10, decimal_places=6, default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="Default model for this type")

    # Usage tracking
    total_requests = models.PositiveIntegerField(default=0)
    total_successful = models.PositiveIntegerField(default=0)
    total_failed = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-is_active', 'name']
        indexes = [
            models.Index(fields=['is_active', 'model_type']),
            models.Index(fields=['provider']),
            models.Index(fields=['is_default']),
        ]
        unique_together = ['name', 'version']

    def __str__(self):
        return f"{self.name} v{self.version} ({self.provider})"

    def save(self, *args, **kwargs):
        # If this model is set as default, unset other defaults of the same type
        if self.is_default:
            AIModel.objects.filter(model_type=self.model_type, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class AIRequest(TimeStampedModel):
    """
    Tracks individual AI requests for monitoring and debugging.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
        ('cancelled', 'Cancelled'),
    )

    # ─── Relations ────────────────────────────────────────────
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_requests'
    )
    model = models.ForeignKey(
        AIModel,
        on_delete=models.PROTECT,
        related_name='requests'
    )

    # ─── Request ─────────────────────────────────────────────
    request_id = models.CharField(max_length=50, unique=True, db_index=True)
    request_type = models.CharField(max_length=50, db_index=True)
    input_data = models.JSONField()
    metadata = models.JSONField(default=dict, blank=True)

    # ─── Response ────────────────────────────────────────────
    output_data = models.JSONField(null=True, blank=True)
    tokens_used = models.PositiveIntegerField(default=0)
    tokens_prompt = models.PositiveIntegerField(default=0)
    tokens_completion = models.PositiveIntegerField(default=0)

    # ─── Performance ─────────────────────────────────────────
    latency_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Response time in milliseconds"
    )
    cost = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=0,
        help_text="Estimated cost of this request"
    )

    # ─── Status ──────────────────────────────────────────────
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    error_code = models.CharField(max_length=50, blank=True)

    # ─── Completion ──────────────────────────────────────────
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # ─── Metadata ─────────────────────────────────────────────
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['model', 'status']),
            models.Index(fields=['request_type']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['request_id']),
        ]

    def __str__(self):
        return f"{self.request_type} - {self.request_id}"

    def save(self, *args, **kwargs):
        if not self.request_id:
            self.request_id = self.generate_request_id()
        self.full_clean()
        super().save(*args, **kwargs)

    def generate_request_id(self):
        return f"AI-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:12].upper()}"

    def clean(self):
        if self.status == 'success' and not self.output_data:
            raise ValidationError("Successful requests must have output_data.")
        if self.status in ['pending', 'processing'] and self.completed_at:
            raise ValidationError("Pending/processing requests cannot have completed_at.")
        if self.status == 'success' and not self.completed_at:
            raise ValidationError("Successful requests must have completed_at.")
        if self.tokens_used > 0 and self.tokens_prompt == 0 and self.tokens_completion == 0:
            raise ValidationError("Tokens_used must equal tokens_prompt + tokens_completion.")

    # ─── Properties ──────────────────────────────────────────
    @property
    def is_successful(self):
        return self.status == 'success'

    @property
    def is_failed(self):
        return self.status in ['failed', 'timeout', 'cancelled']

    @property
    def duration_seconds(self):
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    # ─── Methods ──────────────────────────────────────────────
    def mark_started(self):
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save()

    def mark_success(self, output_data, tokens_prompt=0, tokens_completion=0, latency_ms=0, cost=0):
        self.status = 'success'
        self.output_data = output_data
        self.tokens_prompt = tokens_prompt
        self.tokens_completion = tokens_completion
        self.tokens_used = tokens_prompt + tokens_completion
        self.latency_ms = latency_ms
        self.cost = cost
        self.completed_at = timezone.now()
        self.save()
        # Update model stats
        self.model.total_requests += 1
        self.model.total_successful += 1
        self.model.save()

    def mark_failed(self, error_message, error_code=''):
        self.status = 'failed'
        self.error_message = error_message
        self.error_code = error_code
        self.completed_at = timezone.now()
        self.save()
        self.model.total_requests += 1
        self.model.total_failed += 1
        self.model.save()

    def cancel(self):
        if self.status in ['pending', 'processing']:
            self.status = 'cancelled'
            self.completed_at = timezone.now()
            self.save()
