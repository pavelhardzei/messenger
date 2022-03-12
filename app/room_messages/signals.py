from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import prefetch_related_objects
from django.db.models.signals import post_save
from django.dispatch import receiver
from room_messages.models import Message
from room_messages.serializers import MessageSerializer


@receiver(post_save, sender=Message)
def send_notification(sender, instance, created, **kwargs):
    if not created:
        return None

    msg = MessageSerializer(instance).data
    room = instance.room
    prefetch_related_objects([room], 'users__user')

    channel_layer = get_channel_layer()
    for room_user in room.users.all():
        if instance.sender != room_user.user:
            async_to_sync(channel_layer.group_send)(
                f'user_pk_{room_user.user.pk}',
                {'type': 'send_notification', **msg}
            )
