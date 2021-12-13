from django.db import models
from users.models import UserProfile


class Room(models.Model):
    class RoomType(models.TextChoices):
        open = ('open', 'OPEN')
        closed = ('closed', 'CLOSED')
        private = ('private', 'PRIVATE')

    title = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    room_type = models.CharField(max_length=15, choices=RoomType.choices, default=RoomType.open)

    def __str__(self):
        return self.title


class RoomUser(models.Model):
    class Role(models.TextChoices):
        member = ('member', 'MEMBER')
        moderator = ('moderator', 'MODERATOR')
        owner = ('owner', 'OWNER')

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='users')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='rooms')
    role = models.CharField(max_length=15, choices=Role.choices)

    def __str__(self):
        return f'Room: {self.room}, user: {self.user}'
