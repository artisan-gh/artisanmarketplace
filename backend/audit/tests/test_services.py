from django.test import TestCase
from django.contrib.auth import get_user_model
from audit.services import AuditService
from audit.models import AuditLog

User = get_user_model()


class AuditServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="pass")

    def test_log_create(self):
        log = AuditService.log_create(self.user, None, module="test")
        self.assertEqual(log.action, "CREATE")
        self.assertEqual(log.user, self.user)

    def test_log_delete(self):
        log = AuditService.log_delete(self.user, None, module="test")
        self.assertEqual(log.action, "DELETE")