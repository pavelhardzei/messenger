from django.contrib import admin
from rooms.models import Invitation, Room, RoomUser

admin.site.register(Room)
admin.site.register(RoomUser)
admin.site.register(Invitation)
