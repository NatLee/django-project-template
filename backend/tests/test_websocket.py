"""The ping websocket consumer, through the real ASGI app and the Redis channel layer."""

import json

import pytest
from channels.routing import URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.testing import WebsocketCommunicator

from backend.asgi import application
from backend.routing import websocket_urlpatterns
from tests.conftest import needs_debug

pytestmark = [pytest.mark.django_db(transaction=True), needs_debug]

HEADERS = [(b"origin", b"http://localhost"), (b"host", b"localhost")]


async def connect():
    communicator = WebsocketCommunicator(application, "/ws/ping/", headers=HEADERS)
    connected, _ = await communicator.connect()
    assert connected
    return communicator


async def test_message_comes_back_with_pong():
    communicator = await connect()
    await communicator.send_to(text_data=json.dumps({"message": "hi"}))
    reply = json.loads(await communicator.receive_from(timeout=5))
    assert reply == {"message": "hi Pong!", "action": "ping"}
    await communicator.disconnect()


async def test_message_is_broadcast_to_every_client():
    first, second = await connect(), await connect()
    await first.send_to(text_data=json.dumps({"message": "to all"}))
    for communicator in (first, second):
        assert json.loads(await communicator.receive_from(timeout=5))["message"] == "to all Pong!"
    await first.disconnect()
    await second.disconnect()


async def test_bad_payload_gets_an_error_instead_of_closing():
    communicator = await connect()
    await communicator.send_to(text_data="not json")
    assert json.loads(await communicator.receive_from(timeout=5))["action"] == "error"
    await communicator.disconnect()


async def test_foreign_origin_is_rejected(settings):
    # asgi.py reads ALLOWED_HOSTS once at start-up, so build the same stack with a strict list.
    settings.ALLOWED_HOSTS = ["localhost"]
    strict_app = AllowedHostsOriginValidator(URLRouter(websocket_urlpatterns))
    communicator = WebsocketCommunicator(strict_app, "/ws/ping/", headers=[(b"origin", b"http://evil.example")])
    connected, _ = await communicator.connect()
    assert not connected
