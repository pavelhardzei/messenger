from rest_framework.schemas.openapi import AutoSchema
from users.serializers import UpdateUserSerializer, UserRoomsSerializer


class UserDetailSchema(AutoSchema):
    def get_serializer(self, path, method):
        if method == 'GET':
            return UserRoomsSerializer()
        return UpdateUserSerializer()
