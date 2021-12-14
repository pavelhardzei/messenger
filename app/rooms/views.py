from base.exceptions import LogicError
from base.shortcuts import get_object_or_404_with_message
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rooms.models import Room, RoomUser
from rooms.permissions import IsMember
from rooms.serializers import RoomSerializer, RoomUserSerializer


class RoomList(generics.ListCreateAPIView):
    serializer_class = RoomSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return Room.objects.prefetch_related('users', 'users__user').filter(users__user=self.request.user)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        room_id = response.data['id']

        room_user = RoomUserSerializer(data={'room': room_id, 'user': self.request.user.id,
                                             'role': RoomUser.Role.owner})
        room_user.is_valid(raise_exception=True)
        room_user.save()

        return response


class RoomDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.prefetch_related('users', 'users__user').all()
    serializer_class = RoomSerializer
    permission_classes = (IsMember, )


class EnterRoom(generics.CreateAPIView):
    serializer_class = RoomUserSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        room = get_object_or_404_with_message(Room, 'Room not found', pk=request.data['room'])
        if room.room_type != Room.RoomType.open:
            raise LogicError('Room is not open', status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={**request.data, 'user': self.request.user.id,
                                               'role': RoomUser.Role.member})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data)


class LeaveRoom(generics.CreateAPIView):
    serializer_class = RoomUserSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        room_user = get_object_or_404_with_message(RoomUser.objects.select_related('room'),
                                                   'No user in this room', room=request.data['room'],
                                                   user=self.request.user)
        if room_user.role == RoomUser.Role.owner:
            raise LogicError('Owner cannot leave room without deleting it', status.HTTP_400_BAD_REQUEST)

        response = self.get_serializer(room_user)
        room_user.delete()

        return Response(response.data)
