from rest_framework.schemas.openapi import AutoSchema
from rooms.serializers import EmptySerializer, SetRoleSerializer


class EmptyRequestSchema(AutoSchema):
    def get_request_serializer(self, path, method):
        return EmptySerializer()


class SetRoleSchema(AutoSchema):
    def get_request_serializer(self, path, method):
        return SetRoleSerializer()
