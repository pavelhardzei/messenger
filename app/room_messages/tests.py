from unittest.mock import ANY

from base.constants import DATETIME_FMT
from rest_framework import status
from room_messages.models import Message
from room_messages.permissions import IsSender


def test_message_create(api_client, user1, user3, room1, room_user1):
    api_client.force_authenticate(user1)
    response = api_client.post('/api/message/', {'text': 'some text', 'room': room1.id})
    assert response.status_code == status.HTTP_201_CREATED

    msg = Message.objects.all().first()
    assert response.json() == {'id': ANY, 'text': 'some text', 'room': room1.id,
                               'sender': user1.id,
                               'created_at': f'{msg.created_at.strftime(DATETIME_FMT)}',
                               'updated_at': f'{msg.updated_at.strftime(DATETIME_FMT)}'}

    api_client.force_authenticate(user3)
    response = api_client.post('/api/message/', {'text': 'some text', 'room': room1.id})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_message_update(api_client, user1, room1, message_user1):
    api_client.force_authenticate(user1)
    response = api_client.put(f'/api/message/{message_user1.id}/', {'text': 'updated text'})
    assert response.status_code == status.HTTP_200_OK

    msg = Message.objects.all().first()
    assert response.json() == {'id': ANY, 'text': 'updated text', 'room': room1.id,
                               'sender': user1.id,
                               'created_at': f'{msg.created_at.strftime(DATETIME_FMT)}',
                               'updated_at': f'{msg.updated_at.strftime(DATETIME_FMT)}'}


def test_permissions(rf, user1, message_user1, user2):
    permission = IsSender()

    rf.put(f'/api/message/{message_user1.id}/', {'title': 'updated'})
    rf.user = user1
    assert permission.has_object_permission(rf, None, message_user1)

    rf.user = user2
    assert not permission.has_object_permission(rf, None, message_user1)
