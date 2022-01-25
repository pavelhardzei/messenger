from rest_framework import serializers
from room_messages.serializers import ListMessagesSerializer
from rooms.models import Invitation, Room, RoomUser
from users.serializers import UserSerializer


class RoomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomUser
        fields = ('id', 'room', 'user', 'role')


class ListRoomUserSerializer(RoomUserSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RoomUser
        fields = ('user', 'role')


class RoomSerializer(serializers.ModelSerializer):
    users = ListRoomUserSerializer(read_only=True, many=True)
    messages = ListMessagesSerializer(read_only=True, many=True)

    class Meta:
        model = Room
        fields = ('id', 'title', 'description', 'room_type', 'users', 'messages')


class RoomFindingSerializer(serializers.ModelSerializer):
    users = ListRoomUserSerializer(read_only=True, many=True)

    class Meta:
        model = Room
        fields = ('id', 'title', 'description', 'room_type', 'users')


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ('id', 'room', 'created', 'expiration')

        extra_kwargs = {'created': {'read_only': True}}


class EmptySerializer(serializers.Serializer):
    pass


class SetRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomUser
        fields = ('role', )


class RoomCreateSerializer(serializers.ModelSerializer):
    users = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Room
        fields = ('id', 'title', 'description', 'room_type', 'users')
