from rest_framework import serializers
from rooms.models import Room, RoomUser
from users.serializers import UserSerializer


class RoomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomUser
        fields = ('id', 'room', 'user', 'role')


class ListRoomUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RoomUser
        fields = ('user', )


class RoomSerializer(serializers.ModelSerializer):
    users = ListRoomUserSerializer(read_only=True, many=True)

    class Meta:
        model = Room
        fields = ('id', 'title', 'description', 'open', 'private', 'users')
