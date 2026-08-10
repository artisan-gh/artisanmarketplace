from django.db import models
from django.utils.text import slugify

from common.models import TimeStampedModel
from categories.models import Category, SubCategory


class Service(TimeStampedModel):
    """
    Generic services that artisans can offer.
    Example:
        - House Wiring
        - Pipe Installation
        - Interior Painting
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="services",
        related_query_name="service",
    )

    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        related_name="services",
        related_query_name="service",
        null=True,
        blank=True,
    )

    name = models.CharField(
        max_length=150,
        db_index=True,
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
    )

    description = models.TextField()

    image = models.ImageField(
        upload_to="services/",
        blank=True,
        null=True,
    )

    estimated_duration = models.PositiveIntegerField(
        default=1,
        help_text="Estimated duration in hours.",
    )

    minimum_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Typical minimum market price.",
    )

    maximum_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Typical maximum market price.",
    )

    is_featured = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

        unique_together = (
            "category",
            "name",
        )

        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["category"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["slug"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
