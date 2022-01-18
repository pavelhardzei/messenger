from base.exceptions import LogicError
from base.utils import check
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rooms.models import Invitation, Room, RoomUser
from rooms.permissions import IsHigherRole, IsMember, IsOwner
from rooms.schemas import EmptyRequestSchema, SetRoleSchema, RoomListSchema
from rooms.serializers import InvitationSerializer, RoomFindingSerializer, RoomSerializer, RoomUserSerializer


class RoomList(generics.ListCreateAPIView):
    schema = RoomListSchema(tags=['rooms'])
    serializer_class = RoomSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return Room.objects.prefetch_related('users', 'users__user', 'messages').filter(users__user=self.request.user)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        room_id = response.data['id']

        self.create_room_user(room_id, request.user.id, RoomUser.Role.owner)

        users = request.data['users']
        for user_id in users:
            self.create_room_user(room_id, user_id, RoomUser.Role.member)

        room = get_object_or_404(self.get_queryset(), pk=room_id)

        return Response(self.get_serializer(room).data, status=status.HTTP_201_CREATED)

    def create_room_user(self, room_id, user_id, role):
        room_user = RoomUserSerializer(data={'room': room_id, 'user': user_id, 'role': role})
        room_user.is_valid(raise_exception=True)
        room_user.save()


class RoomDetail(generics.RetrieveUpdateDestroyAPIView):
    schema = AutoSchema(tags=['rooms'])
    queryset = Room.objects.prefetch_related('users', 'users__user', 'messages').all()
    serializer_class = RoomSerializer
    permission_classes = (IsMember, )


class RoomFinding(generics.ListAPIView):
    schema = AutoSchema(tags=['rooms'])
    serializer_class = RoomFindingSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        check(self.request.query_params.dict().keys(), Room.query_params())

        params = {f'{k}__contains': v for k, v in self.request.query_params.dict().items()}
        return Room.objects.prefetch_related('users', 'users__user').filter(**params)[:10]


class EnterRoom(generics.GenericAPIView):
    schema = EmptyRequestSchema(tags=['rooms'])
    serializer_class = RoomUserSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def put(self, request, *args, **kwargs):
        room_user = RoomUser.objects.filter(room=self.kwargs['pk'], user=request.user.id).first()
        if room_user:
            return Response(self.get_serializer(room_user).data)

        room = get_object_or_404(Room, pk=self.kwargs['pk'])
        if not room.is_open:
            raise LogicError('Room is not open', status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data={'room': self.kwargs['pk'], 'user': request.user.id,
                                               'role': RoomUser.Role.member})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LeaveRoom(generics.DestroyAPIView):
    schema = AutoSchema(tags=['rooms'])
    serializer_class = RoomUserSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self):
        obj = get_object_or_404(RoomUser, room=self.kwargs['pk'], user=self.request.user)
        self.check_object_permissions(self.request, obj)

        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_owner:
            raise LogicError('Owner cannot leave room without deleting it', status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RemoveUser(generics.DestroyAPIView):
    schema = AutoSchema(tags=['rooms'])
    serializer_class = RoomUserSerializer
    permission_classes = (IsHigherRole, )

    def get_object(self):
        obj = get_object_or_404(RoomUser, room=self.kwargs['room_pk'], user=self.kwargs['user_pk'])
        self.check_object_permissions(self.request, obj)

        return obj


class SetRole(generics.GenericAPIView):
    schema = SetRoleSchema(tags=['rooms'])
    serializer_class = RoomUserSerializer
    permission_classes = (IsOwner, )

    def put(self, request, *args, **kwargs):
        instance = get_object_or_404(RoomUser, room=self.kwargs['room_pk'], user=self.kwargs['user_pk'])
        self.check_object_permissions(request, instance)

        serializer = self.get_serializer(instance, data={'role': request.data['role']}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class MakeInvitation(generics.CreateAPIView):
    schema = AutoSchema(tags=['invitations'])
    serializer_class = InvitationSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        if Room.objects.filter(pk=request.data['room'], room_type=Room.RoomType.closed).exists():
            return Response('Room is closed', status=status.HTTP_403_FORBIDDEN)
        if not RoomUser.objects.filter(room=request.data['room'], user=request.user).exists():
            return Response('You are not a member', status=status.HTTP_403_FORBIDDEN)

        return super().post(request, *args, **kwargs)


class AcceptInvitation(generics.CreateAPIView):
    schema = EmptyRequestSchema(tags=['invitations'])
    serializer_class = RoomUserSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        uuid4 = self.kwargs['uuid4']
        inv = get_object_or_404(Invitation.objects.select_related('room'), pk=uuid4)

        if inv.expired:
            inv.delete()
            return Response({'error_message': 'Invitation is expired'}, status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(data={'room': inv.room.id, 'user': self.request.user.id,
                                               'role': RoomUser.Role.member})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        inv.delete()

        return Response(serializer.data)
