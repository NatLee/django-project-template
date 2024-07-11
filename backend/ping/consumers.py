from channels.generic.websocket import AsyncWebsocketConsumer
import json

class PingConsumer(AsyncWebsocketConsumer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = 'ping'
    
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "send_ping", # this is the method name in this consumer
                "message": message + " Pong!"
            }
        )

    async def send_ping(self, event):
        message = event["message"]
        await self.send(
            text_data=json.dumps(
                {
                    'message': message,
                    'action': 'ping'
                }
            )
        )

