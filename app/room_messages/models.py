from django.db import models
from django.utils import timezone
from rooms.models import Room
from users.models import UserProfile


class Message(models.Model):
    text = models.CharField(max_length=300)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
