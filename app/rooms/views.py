import datetime

from base.exceptions import LogicError
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rooms.models import Invitation, Room, RoomUser
from rooms.permissions import IsHigherRole, IsMember, IsOwner
from rooms.serializers import InvitationSerializer, RoomSerializer, RoomUserSerializer


class RoomList(generics.ListCreateAPIView):
    serializer_class = RoomSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return Room.objects.prefetch_related('users', 'users__user').filter(users__user=self.request.user)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        room_id = response.data['id']

        self.create_room_user(room_id, request.user.id, RoomUser.Role.owner)

        users = request.data['users']
        for user_id in users:
            self.create_room_user(room_id, user_id, RoomUser.Role.member)

        room = get_object_or_404(Room.objects.prefetch_related('users', 'users__user'), pk=room_id)

        return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

    def create_room_user(self, room_id, user_id, role):
        room_user = RoomUserSerializer(data={'room': room_id, 'user': user_id, 'role': role})
        room_user.is_valid(raise_exception=True)
        room_user.save()


class RoomDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.prefetch_related('users', 'users__user').all()
    serializer_class = RoomSerializer
    permission_classes = (IsMember, )


class EnterRoom(generics.CreateAPIView):
    serializer_class = RoomUserSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        room = get_object_or_404(Room, pk=request.data['room'])
        if not room.is_open:
            raise LogicError('Room is not open', status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data={'room': request.data['room'], 'user': self.request.user.id,
                                               'role': RoomUser.Role.member})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data)


class LeaveRoom(generics.CreateAPIView):
    serializer_class = RoomUserSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        room_user = get_object_or_404(RoomUser, room=request.data['room'], user=self.request.user)
        if room_user.is_owner:
            raise LogicError('Owner cannot leave room without deleting it', status.HTTP_403_FORBIDDEN)

        response = self.get_serializer(room_user)
        room_user.delete()

        return Response(response.data)


class RemoveUser(generics.CreateAPIView):
    serializer_class = RoomUserSerializer
    permission_classes = (IsHigherRole, )

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(RoomUser, room=request.data['room'], user=request.data['user'])
        self.check_object_permissions(request, obj)
        obj.delete()

        serializer = self.get_serializer(obj)
        return Response(serializer.data)


class SetRole(generics.CreateAPIView):
    serializer_class = RoomUserSerializer
    permission_classes = (IsOwner, )

    def post(self, request, *args, **kwargs):
        instance = get_object_or_404(RoomUser, room=request.data['room'], user=request.data['user'])
        self.check_object_permissions(request, instance)

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class MakeInvitation(generics.CreateAPIView):
    serializer_class = InvitationSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        if Room.objects.filter(pk=request.data['room'], room_type=Room.RoomType.closed).exists():
            return Response('Room is closed', status=status.HTTP_403_FORBIDDEN)
        if not RoomUser.objects.filter(room=request.data['room'], user=request.user).exists():
            return Response('You are not a member', status=status.HTTP_403_FORBIDDEN)

        return super().post(request, *args, **kwargs)


class AcceptInvitation(generics.CreateAPIView):
    serializer_class = RoomUserSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        uuid4 = self.kwargs['uuid4']
        inv = get_object_or_404(Invitation.objects.select_related('room'), pk=uuid4)

        if datetime.datetime.now() - inv.created.replace(tzinfo=None) > inv.expiration:
            inv.delete()
            return Response('Invitation is expired', status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(data={'room': inv.room.id, 'user': self.request.user.id,
                                               'role': RoomUser.Role.member})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        inv.delete()

        return Response(serializer.data)
