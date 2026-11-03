import json

from channels.generic.websocket import AsyncWebsocketConsumer


class PingConsumer(AsyncWebsocketConsumer):
    """Echo every message, with " Pong!" added, to everyone connected to the ping group.

    The message travels through the channel layer (Redis), so this also proves that
    several server processes can talk to each other's websocket clients.
    """

    group_name = "ping"

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            message = json.loads(text_data)["message"]
        except (TypeError, ValueError, KeyError):
            await self.send(text_data=json.dumps({"action": "error", "message": 'Send JSON like {"message": "hi"}'}))
            return
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "send_ping", "message": f"{message} Pong!"},  # "type" names the handler below
        )

    async def send_ping(self, event):
        await self.send(text_data=json.dumps({"message": event["message"], "action": "ping"}))
