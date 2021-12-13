from rest_framework import permissions
from rooms.models import RoomUser


class IsMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            roles = (RoomUser.Role.owner, )
        elif request.method in ('PUT', 'PATCH'):
            roles = (RoomUser.Role.owner, RoomUser.Role.moderator)
        else:
            roles = (RoomUser.Role.owner, RoomUser.Role.moderator, RoomUser.Role.member)

        return request.user.is_superuser or RoomUser.objects.filter(room=obj, user=request.user,
                                                                    role__in=roles).exists()
