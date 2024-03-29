import datetime

import pyotp
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.authtoken.views import Token
from rest_framework.exceptions import ValidationError
from rooms.models import Room, RoomUser
from users.models import UserProfile


class ListRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('id', 'title', 'description', 'room_type')


class ListUserRoomSerializer(serializers.ModelSerializer):
    room = ListRoomSerializer(read_only=True)

    class Meta:
        model = RoomUser
        fields = ('room', 'role')


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('email', 'user_name', 'full_name', 'date_of_birth')

    def validate_date_of_birth(self, value):
        date_of_birth = datetime.datetime.strptime(str(value), '%Y-%m-%d').date()
        if (datetime.date.today() - date_of_birth).days < 0:
            raise ValidationError({'error_message': 'Invalid age'})
        return value


class UserSerializer(UpdateUserSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'email', 'user_name', 'full_name', 'date_of_birth', 'date_joined', 'password')

        extra_kwargs = {'password': {'write_only': True},
                        'date_joined': {'read_only': True}}

    def create(self, validated_data):
        user = UserProfile(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        Token.objects.create(user=user)

        return user


class UserRoomsSerializer(UserSerializer):
    rooms = ListUserRoomSerializer(read_only=True, many=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'email', 'user_name', 'full_name', 'date_of_birth', 'date_joined', 'rooms')

        extra_kwargs = {'date_joined': {'read_only': True}}


class PasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    password_rep = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ('old_password', 'password', 'password_rep')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_rep']:
            raise ValidationError({'message_error': 'Passwords did not match'})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError({'message_error': 'Old password is not correct'})
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    user_name = serializers.CharField(required=False)
    password = serializers.CharField()
    totp = serializers.CharField(required=False)

    def validate(self, attrs):
        email = attrs.get('email')
        user_name = attrs.get('user_name')
        password = attrs.get('password')
        totp = attrs.get('totp')

        if not (email or user_name) or not password:
            raise ValidationError({'error_message': 'Must include email + pwd or user_name + pwd'})

        if email:
            user = get_object_or_404(UserProfile, email=email)
        else:
            user = get_object_or_404(UserProfile, user_name=user_name)

        if not (user.check_password(password) and user.is_active):
            raise ValidationError({'error_message': 'Unable to log in with provided credentials'})

        if user.secret and not pyotp.TOTP(user.secret).verify(totp):
            raise ValidationError({'error_message': 'Invalid one-time password'})

        attrs['user'] = user
        return attrs


class UserTokenSerializer(serializers.Serializer):
    user = UserRoomsSerializer(read_only=True)
    token = serializers.CharField()


class TOTPSerializer(serializers.Serializer):
    secret = serializers.URLField()


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UserListSerializer(serializers.Serializer):
    users = serializers.ListField(child=serializers.IntegerField())


class UsersOnlineDictSerializer(serializers.Serializer):
    users = serializers.DictField(child=serializers.BooleanField())
