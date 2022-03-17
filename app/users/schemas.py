from rest_framework.schemas.openapi import AutoSchema
from rooms.serializers import EmptySerializer
from users.serializers import (TOTPSerializer, UpdateUserSerializer, UserListSerializer, UserRoomsSerializer,
                               UsersOnlineDictSerializer, UserTokenSerializer)


class UserDetailSchema(AutoSchema):
    def get_serializer(self, path, method):
        if method == 'GET':
            return UserRoomsSerializer()
        return UpdateUserSerializer()


class UserSignInSchema(AutoSchema):
    def get_response_serializer(self, path, method):
        return UserTokenSerializer()


class TOTPSchema(AutoSchema):
    def get_request_serializer(self, path, method):
        return EmptySerializer()

    def get_response_serializer(self, path, method):
        return TOTPSerializer()


class UsersOnlineSchema(AutoSchema):
    def get_request_serializer(self, path, method):
        return UserListSerializer()

    def get_response_serializer(self, path, method):
        return UsersOnlineDictSerializer()
