from django.db import models
from django.utils.text import slugify

from common.models import TimeStampedModel


class Category(TimeStampedModel):
    """
    Main service categories.
    Example:
        - Plumbing
        - Electrical
        - Carpentry
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="React icon name or CSS icon class.",
    )

    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SubCategory(TimeStampedModel):
    """
    Service subcategories.

    Example:
        Category: Plumbing
            - Pipe Installation
            - Leak Repairs
            - Drain Cleaning
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories",
        related_query_name="subcategory",
    )

    name = models.CharField(
        max_length=100,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["category", "name"]
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"
        unique_together = ("category", "name")
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.category.name} → {self.name}"
