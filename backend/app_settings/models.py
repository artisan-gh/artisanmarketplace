from django.db import models
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from common.models import TimeStampedModel


class AppSetting(TimeStampedModel):
    """
    System-wide configuration settings.
    """

    class DataType(models.TextChoices):
        STRING = 'STRING', 'String'
        INTEGER = 'INTEGER', 'Integer'
        FLOAT = 'FLOAT', 'Float'
        BOOLEAN = 'BOOLEAN', 'Boolean'
        JSON = 'JSON', 'JSON'
        LIST = 'LIST', 'List'
        EMAIL = 'EMAIL', 'Email'
        URL = 'URL', 'URL'

    class SettingGroup(models.TextChoices):
        GENERAL = 'GENERAL', 'General'
        PAYMENT = 'PAYMENT', 'Payment'
        EMAIL = 'EMAIL', 'Email'
        NOTIFICATION = 'NOTIFICATION', 'Notification'
        SECURITY = 'SECURITY', 'Security'
        FEATURES = 'FEATURES', 'Features'
        INTEGRATION = 'INTEGRATION', 'Integration'
        SEO = 'SEO', 'SEO'
        SOCIAL = 'SOCIAL', 'Social'

    key = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique identifier for the setting (e.g., 'site_name')"
    )

    value = models.TextField(
        help_text="The value of the setting (stored as string, parsed according to data_type)"
    )

    data_type = models.CharField(
        max_length=10,
        choices=DataType.choices,
        default=DataType.STRING,
        help_text="Data type for parsing the value"
    )

    group = models.CharField(
        max_length=20,
        choices=SettingGroup.choices,
        default=SettingGroup.GENERAL,
        db_index=True,
        help_text="Group for organising settings"
    )

    description = models.TextField(blank=True, help_text="Purpose of this setting")

    is_public = models.BooleanField(
        default=False,
        help_text="Whether this setting is exposed to the public API"
    )

    is_editable = models.BooleanField(
        default=True,
        help_text="Whether this setting can be edited via the admin"
    )

    is_required = models.BooleanField(
        default=False,
        help_text="Whether this setting must have a value"
    )

    options = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional options (e.g., {'min': 0, 'max': 100, 'choices': [...]})"
    )

    class Meta:
        ordering = ['group', 'key']
        indexes = [
            models.Index(fields=['group']),
            models.Index(fields=['key']),
            models.Index(fields=['is_public']),
        ]
        verbose_name_plural = "App Settings"

    def __str__(self):
        return f"{self.key} = {self.value}"

    def clean(self):
        # Validate value based on data_type
        if self.value:
            try:
                self._parse_value()
            except (ValueError, TypeError) as e:
                raise ValidationError({'value': f"Invalid value for {self.get_data_type_display()}: {e}"})

        # Validate required
        if self.is_required and not self.value:
            raise ValidationError({'value': "This setting is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # Invalidate cache on save
        cache.delete(f'setting_{self.key}')

    def _parse_value(self):
        """Parse the stored value according to data_type."""
        if not self.value:
            return None
        if self.data_type == self.DataType.STRING:
            return str(self.value)
        elif self.data_type == self.DataType.INTEGER:
            return int(self.value)
        elif self.data_type == self.DataType.FLOAT:
            return float(self.value)
        elif self.data_type == self.DataType.BOOLEAN:
            if self.value.lower() in ('true', '1', 'yes', 'on'):
                return True
            elif self.value.lower() in ('false', '0', 'no', 'off'):
                return False
            raise ValueError("Invalid boolean value")
        elif self.data_type == self.DataType.JSON:
            import json
            return json.loads(self.value)
        elif self.data_type == self.DataType.LIST:
            import json
            data = json.loads(self.value)
            if not isinstance(data, list):
                raise ValueError("Value must be a list")
            return data
        elif self.data_type == self.DataType.EMAIL:
            from django.core.validators import validate_email
            validate_email(self.value)
            return self.value
        elif self.data_type == self.DataType.URL:
            from django.core.validators import URLValidator
            URLValidator()(self.value)
            return self.value
        return self.value

    @property
    def parsed_value(self):
        """Get the value parsed to its proper Python type."""
        return self._parse_value()

    @classmethod
    def get(cls, key, default=None):
        """Get a setting value by key, with caching."""
        cache_key = f'setting_{key}'
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            setting = cls.objects.get(key=key)
            value = setting.parsed_value
            cache.set(cache_key, value, 3600)  # cache for 1 hour
            return value
        except cls.DoesNotExist:
            return default

    @classmethod
    def get_group(cls, group):
        """Get all settings for a group."""
        return {
            setting.key: setting.parsed_value
            for setting in cls.objects.filter(group=group)
        }

    @classmethod
    def get_public(cls):
        """Get all public settings."""
        return {
            setting.key: setting.parsed_value
            for setting in cls.objects.filter(is_public=True)
        }
