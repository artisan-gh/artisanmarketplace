import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    Each authenticated user gets their own group: user_{user_id}
    """
    
    async def connect(self):
        """
        Called when the WebSocket is handshaking as part of the connection process.
        """
        self.user = self.scope.get("user")
        
        # Reject unauthenticated connections
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        # Create a unique group for this user
        self.group_name = f"user_{self.user.id}"
        
        # Add user to their group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        # Accept the connection
        await self.accept()
        
        # Send unread count on connection
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": f"Connected to notifications for user {self.user.id}",
            "unread_count": unread_count
        }))

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes.
        """
        # Remove user from their group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        Called when a message is received from the client.
        """
        try:
            data = json.loads(text_data)
            action = data.get("action")
            
            if action == "mark_read":
                notification_id = data.get("notification_id")
                if notification_id:
                    await self.mark_notification_read(notification_id)
                    await self.send(text_data=json.dumps({
                        "type": "marked_read",
                        "notification_id": notification_id
                    }))
                    
            elif action == "mark_all_read":
                count = await self.mark_all_read()
                await self.send(text_data=json.dumps({
                    "type": "marked_all_read",
                    "count": count
                }))
                
            elif action == "get_unread_count":
                count = await self.get_unread_count()
                await self.send(text_data=json.dumps({
                    "type": "unread_count",
                    "count": count
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Invalid JSON"
            }))

    # ─── Send notification (called from outside) ──────────────

    async def send_notification(self, event):
        """
        Called when a notification is sent to this user's group.
        This is triggered by the `notification_created` signal or manually.
        """
        data = event.get("data", {})
        
        # Send to WebSocket client
        await self.send(text_data=json.dumps({
            "type": "new_notification",
            "notification": data
        }))

    # ─── Database operations ──────────────────────────────────

    @database_sync_to_async
    def get_unread_count(self):
        """Get unread notification count for the user."""
        return Notification.objects.filter(
            user=self.user,
            is_read=False
        ).count()

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark a specific notification as read."""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False

    @database_sync_to_async
    def mark_all_read(self):
        """Mark all notifications as read for the user."""
        count = Notification.objects.filter(
            user=self.user,
            is_read=False
        ).update(is_read=True)
        return count