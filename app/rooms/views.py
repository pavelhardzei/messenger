from django.db import transaction
from rest_framework import generics, permissions
from rooms.models import Room, RoomUser
from rooms.serializers import RoomSerializer, RoomUserSerializer


class RoomList(generics.ListCreateAPIView):
    serializer_class = RoomSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return Room.objects.prefetch_related('users').filter(users__user=self.request.user)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        room_id = response.data['id']

        room_user = RoomUserSerializer(data={'room': room_id, 'user': self.request.user.id,
                                             'role': RoomUser.Role.owner})
        room_user.is_valid(raise_exception=True)
        room_user.save()

        return response
