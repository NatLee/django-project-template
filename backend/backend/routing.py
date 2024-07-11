
from django.urls import re_path
from django.conf import settings

from ping import consumers

websocket_urlpatterns = []

if settings.DEBUG:
    websocket_urlpatterns += [
        re_path(r"ws/ping/$", consumers.PingConsumer.as_asgi()),
    ]
