from django.db import models
from django.utils import timezone


class AuditLogQuerySet(models.QuerySet):

    def today(self):
        today = timezone.now().date()
        return self.filter(created_at__date=today)

    def successful(self):
        return self.filter(success=True)

    def failed(self):
        return self.filter(success=False)

    def for_user(self, user):
        return self.filter(user=user)

    def for_module(self, module):
        return self.filter(module=module)

    def for_action(self, action):
        return self.filter(action=action)

    def for_object(self, instance):
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(instance)
        return self.filter(content_type=ct, object_id=str(instance.pk))

    def critical(self):
        return self.filter(severity='CRITICAL')

    def high(self):
        return self.filter(severity='HIGH')

    def medium(self):
        return self.filter(severity='MEDIUM')

    def low(self):
        return self.filter(severity='LOW')

    def not_archived(self):
        return self.filter(archived=False)

    def archived(self):
        return self.filter(archived=True)


class AuditLogManager(models.Manager):
    def get_queryset(self):
        return AuditLogQuerySet(self.model, using=self._db)

    def today(self):
        return self.get_queryset().today()

    def successful(self):
        return self.get_queryset().successful()

    def failed(self):
        return self.get_queryset().failed()

    def for_user(self, user):
        return self.get_queryset().for_user(user)

    def for_module(self, module):
        return self.get_queryset().for_module(module)

    def for_action(self, action):
        return self.get_queryset().for_action(action)

    def for_object(self, instance):
        return self.get_queryset().for_object(instance)

    def not_archived(self):
        return self.get_queryset().not_archived()