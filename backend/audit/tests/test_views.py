from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class AuditLogViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(email="admin@example.com", password="pass")
        self.audit_url = reverse("audit:audit-log-list")

    def test_unauthorized_access(self):
        response = self.client.get(self.audit_url)
        self.assertEqual(response.status_code, 401)

    def test_authorized_access(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.audit_url)
        self.assertEqual(response.status_code, 200)