import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django_redis import get_redis_connection


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_pk = ''
        self.room_group_name = ''

    async def connect(self):
        self.room_pk = self.scope['url_route']['kwargs']['pk']
        if not await self.user_belongs():
            await self.close()

        self.room_group_name = f'room_pk_{self.room_pk}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        data = await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                **data
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'text': event['text'],
            'room': event['room'],
            'sender': event['sender'],
            'created_at': event['created_at'],
            'updated_at': event['updated_at']
        }))

    @database_sync_to_async
    def user_belongs(self):
        from rooms.models import RoomUser
        return RoomUser.objects.filter(room=self.room_pk, user=self.scope['user'].pk).exists()

    @database_sync_to_async
    def save_message(self, message):
        from room_messages.serializers import MessageSerializer

        serializer = MessageSerializer(data={'text': message, 'room': self.room_pk})
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=self.scope['user'])

        return serializer.data


class UserConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_group_name = ''

        self.conn = get_redis_connection('default')
        self.storage = 'cache:users:online'

    async def connect(self):
        self.user_group_name = f"user_pk_{self.scope['user'].pk}"

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        self.conn.sadd(self.storage, self.scope['user'].pk)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

        self.conn.srem(self.storage, self.scope['user'].pk)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'text': event['text'],
            'room': event['room'],
            'sender': event['sender'],
            'created_at': event['created_at'],
            'updated_at': event['updated_at']
        }))
