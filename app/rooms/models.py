from django.db import models
from users.models import UserProfile


class Room(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    open = models.BooleanField(default=True)
    private = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class RoomUser(models.Model):
    class Role(models.TextChoices):
        member = ('member', 'MEMBER')
        moderator = ('moderator', 'MODERATOR')
        owner = ('owner', 'OWNER')

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    role = models.CharField(max_length=15, choices=Role.choices)

    def __str__(self):
        return f'Room: {self.room}, user: {self.user}'
