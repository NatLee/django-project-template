"""Websocket routes. NGINX forwards /ws to Django (see nginx/default.conf)."""

from django.conf import settings
from django.urls import re_path

websocket_urlpatterns = []

# The ping example lives next to the other development pages.
if settings.DEBUG:
    from ping import consumers

    websocket_urlpatterns += [
        re_path(r"ws/ping/$", consumers.PingConsumer.as_asgi()),
    ]
