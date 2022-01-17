from rest_framework.schemas.openapi import AutoSchema
from users.serializers import UpdateUserSerializer, UserRoomsSerializer, UserSignInSerializer


class UserDetailSchema(AutoSchema):
    def get_serializer(self, path, method):
        if method == 'GET':
            return UserRoomsSerializer()
        return UpdateUserSerializer()


class UserSignInSchema(AutoSchema):
    def get_response_serializer(self, path, method):
        return UserSignInSerializer()
