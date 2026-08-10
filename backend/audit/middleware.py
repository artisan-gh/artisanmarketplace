import time
import uuid
from threading import local
from django.utils.deprecation import MiddlewareMixin

_user_locals = local()


def get_current_user():
    return getattr(_user_locals, 'user', None)


def get_current_request():
    return getattr(_user_locals, 'request', None)


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware that:
      - stores the current user and request in thread‑locals
      - injects a correlation ID if missing
      - measures request duration and attaches it to the request
    """
    def process_request(self, request):
        if hasattr(request, 'user'):
            _user_locals.user = request.user
            _user_locals.request = request

        correlation_id = request.META.get("HTTP_X_CORRELATION_ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
            request.META["HTTP_X_CORRELATION_ID"] = correlation_id

        request._audit_start_time = time.time()

    def process_response(self, request, response):
        start = getattr(request, '_audit_start_time', None)
        if start:
            duration_ms = int((time.time() - start) * 1000)
            response._audit_duration_ms = duration_ms

        if hasattr(_user_locals, 'user'):
            del _user_locals.user
        if hasattr(_user_locals, 'request'):
            del _user_locals.request

        return response

    def process_exception(self, request, exception):
        if hasattr(_user_locals, 'user'):
            del _user_locals.user
        if hasattr(_user_locals, 'request'):
            del _user_locals.request
        return None