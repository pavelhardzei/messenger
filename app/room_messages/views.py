from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from room_messages.models import Message
from room_messages.permissions import IsSender
from room_messages.serializers import MessageSerializer
from rooms.models import RoomUser


class MessageCreate(generics.CreateAPIView):
    schema = AutoSchema(tags=['messages'])
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        if not RoomUser.objects.filter(room=request.data['room'], user=request.user.id).exists():
            return Response({'error_message': 'You are not in this room'}, status=status.HTTP_403_FORBIDDEN)

        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    schema = AutoSchema(tags=['messages'])
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (IsSender, )
