"""ASGI entry point: HTTP goes to Django, websockets go to Channels consumers.

https://docs.djangoproject.com/en/stable/howto/deployment/asgi/
https://channels.readthedocs.io/en/stable/deploying.html
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
# Set up Django (settings + app registry) before importing anything that touches models.
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402

from backend.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns))),
    }
)
