from django.urls import re_path
from ping import consumers

websocket_urlpatterns = [
    re_path(r"ws/ping/$", consumers.PingConsumer.as_asgi()),
]