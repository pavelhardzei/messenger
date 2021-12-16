from django.shortcuts import get_object_or_404
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


class IsHigherRole(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        room_user = get_object_or_404(RoomUser, room=obj.room, user=request.user)

        return RoomUser.Role.values.index(room_user.role) > RoomUser.Role.values.index(obj.role)


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return RoomUser.objects.filter(room=obj.room, user=request.user,
                                       role=RoomUser.Role.owner).exists() and obj.user != request.user
