"""
ASGI config for artisan marketplace project.
Exposes the ASGI callable as a module-level variable named `application`.
"""

import os

from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# ─── 1. Get Django's ASGI application first ────────────────
django_asgi_app = get_asgi_application()

# ─── 2. Import Channels after Django setup ──────────────────
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# ─── 3. Import your consumer ─────────────────────────────────
from notifications.consumers import NotificationConsumer

# ─── 4. WebSocket URL patterns ───────────────────────────────
websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]

# ─── 5. Application router ────────────────────────────────────
application = ProtocolTypeRouter({
    # HTTP traffic → Django
    "http": django_asgi_app,

    # WebSocket traffic → Channels with auth & origin validation
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
