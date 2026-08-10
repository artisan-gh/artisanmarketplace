import os
import uuid
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.utils import timezone
from common.models import TimeStampedModel


class MediaFile(TimeStampedModel):
    """
    Central media file model with support for multiple storage backends.
    """

    class FileCategory(models.TextChoices):
        AVATAR = 'AVATAR', 'Avatar'
        PORTFOLIO = 'PORTFOLIO', 'Portfolio'
        SERVICE = 'SERVICE', 'Service'
        CHAT = 'CHAT', 'Chat Attachment'
        DOCUMENT = 'DOCUMENT', 'Document'
        REPORT = 'REPORT', 'Report'
        OTHER = 'OTHER', 'Other'

    # ─── User ──────────────────────────────────────────────────
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='media_files'
    )

    # ─── Generic relation ─────────────────────────────────────
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional reference to the object this file is attached to"
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # ─── File ──────────────────────────────────────────────────
    file = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        max_length=500,
        help_text="The actual file"
    )

    # ─── Metadata ──────────────────────────────────────────────
    file_name = models.CharField(max_length=255, blank=True, help_text="Original filename")
    file_size = models.PositiveIntegerField(default=0, help_text="Size in bytes")
    mime_type = models.CharField(max_length=100, blank=True)
    file_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Detected file type (image, video, document, etc.)"
    )

    category = models.CharField(
        max_length=20,
        choices=FileCategory.choices,
        default=FileCategory.OTHER
    )

    # ─── Image-specific ───────────────────────────────────────
    width = models.PositiveIntegerField(null=True, blank=True, help_text="Image width in pixels")
    height = models.PositiveIntegerField(null=True, blank=True, help_text="Image height in pixels")
    thumbnail = models.ImageField(
        upload_to='thumbnails/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Auto-generated thumbnail"
    )

    # ─── Access Control ──────────────────────────────────────
    is_public = models.BooleanField(default=False, help_text="Whether the file is publicly accessible")
    expires_at = models.DateTimeField(null=True, blank=True, help_text="If set, file will be deleted after this date")

    # ─── Status ──────────────────────────────────────────────
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'category']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['file_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
        verbose_name_plural = "Media Files"

    def __str__(self):
        return self.file_name or str(self.file.name)

    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = os.path.basename(self.file.name)
        if self.file:
            self.file_size = self.file.size
            self.mime_type = self.file.file.content_type if hasattr(self.file.file, 'content_type') else ''
            # Detect file type
            if self.mime_type:
                if self.mime_type.startswith('image/'):
                    self.file_type = 'image'
                elif self.mime_type.startswith('video/'):
                    self.file_type = 'video'
                elif self.mime_type.startswith('application/pdf'):
                    self.file_type = 'pdf'
                elif self.mime_type.startswith('text/') or 'document' in self.mime_type:
                    self.file_type = 'document'
                else:
                    self.file_type = 'other'
            else:
                self.file_type = 'other'

            # Generate thumbnail if image
            if self.file_type == 'image':
                self.generate_thumbnail()

        self.full_clean()
        super().save(*args, **kwargs)

    def generate_thumbnail(self, size=(150, 150)):
        """Generate a thumbnail for image files."""
        try:
            img = Image.open(self.file)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            thumb_io = BytesIO()
            img_format = img.format or 'JPEG'
            if img_format.upper() == 'PNG':
                img.save(thumb_io, format='PNG')
            else:
                img.save(thumb_io, format='JPEG', quality=85)
            thumb_file = ContentFile(thumb_io.getvalue(), f"thumb_{self.file_name}")
            self.thumbnail.save(thumb_file.name, thumb_file, save=False)
            # Store dimensions
            self.width, self.height = img.size
        except Exception:
            pass  # Fail silently if thumbnail generation fails

    @property
    def url(self):
        """Get the file URL."""
        if self.file:
            return self.file.url
        return None

    @property
    def thumbnail_url(self):
        """Get the thumbnail URL."""
        if self.thumbnail:
            return self.thumbnail.url
        return None

    @property
    def is_expired(self):
        """Check if the file has expired."""
        return self.expires_at and timezone.now() > self.expires_at

    def soft_delete(self):
        """Soft delete the file."""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        """Hard delete the file (remove from storage)."""
        if self.file:
            self.file.delete(save=False)
        if self.thumbnail:
            self.thumbnail.delete(save=False)
        self.delete()
