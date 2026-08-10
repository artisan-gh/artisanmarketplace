from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "audit"
    verbose_name = "Audit"

    def ready(self):
        # Import signals to ensure they're registered
        import audit.signals  # noqa
