from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from audit.middleware import AuditMiddleware

User = get_user_model()


class AuditMiddlewareTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="pass")
        self.factory = RequestFactory()

    def test_middleware_stores_user(self):
        request = self.factory.get("/")
        request.user = self.user
        middleware = AuditMiddleware(lambda req: None)
        middleware.process_request(request)
        from audit.middleware import _user_locals
        self.assertEqual(_user_locals.user, self.user)