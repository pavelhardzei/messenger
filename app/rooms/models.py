import datetime
import uuid

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

    @property
    def is_open(self):
        return self.room_type == self.RoomType.open

    def __str__(self):
        return self.title

    @staticmethod
    def query_params():
        return ('title', 'description', 'room_type')


class RoomUser(models.Model):
    class Role(models.TextChoices):
        member = ('member', 'MEMBER')
        moderator = ('moderator', 'MODERATOR')
        owner = ('owner', 'OWNER')

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='users')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='rooms')
    role = models.CharField(max_length=15, choices=Role.choices)

    class Meta:
        unique_together = ('room', 'user')

    @property
    def is_owner(self):
        return self.role == self.Role.owner

    def __str__(self):
        return f'Room: {self.room}, user: {self.user}'


class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='invitations')
    created = models.DateTimeField(default=datetime.datetime.utcnow)
    expiration = models.DurationField(default=datetime.timedelta(days=1))

    @property
    def expired(self):
        return datetime.datetime.now() - self.created.replace(tzinfo=None) > self.expiration
