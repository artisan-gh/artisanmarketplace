from django.test import TestCase
from django.contrib.auth import get_user_model
from audit.models import AuditLog
from audit.services import AuditService

User = get_user_model()


class AuditLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="pass")

    def test_audit_log_creation(self):
        log = AuditLog.objects.create(
            user=self.user,
            action="CREATE",
            module="incidents",
            object_repr="Test Incident",
        )
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, "CREATE")
        self.assertEqual(log.module, "incidents")
        self.assertEqual(log.object_repr, "Test Incident")
        self.assertTrue(log.success)

    def test_audit_service_log_create(self):
        log = AuditService.log_create(self.user, instance=None, module="test")
        self.assertEqual(log.action, "CREATE")
        self.assertEqual(log.module, "test")