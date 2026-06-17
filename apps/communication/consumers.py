import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']

        # Verify the user is a participant in this conversation
        allowed = await self.user_can_access(self.conversation_id)
        if not allowed:
            await self.close()
            return

        self.room_group_name = f'chat_{self.conversation_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get('content', '')
        if not content.strip():
            return

        message = await self.save_message(content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': message.id,
                'sender': message.sender_id,
                'sender_email': message.sender.email,
                'content': content,
                'is_read': False,
                'created_at': message.created_at.isoformat(),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'sender': event['sender'],
            'sender_email': event['sender_email'],
            'content': event['content'],
            'is_read': event['is_read'],
            'created_at': event['created_at'],
        }))

    @database_sync_to_async
    def user_can_access(self, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return False
        if self.user.role == 'admin' or self.user.is_superuser:
            return True
        return hasattr(self.user, 'seller_profile') and \
            conversation.seller_id == self.user.seller_profile.id

    @database_sync_to_async
    def save_message(self, content):
        conversation = Conversation.objects.get(id=self.conversation_id)
        return Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content
        )
