from rest_framework import status
from room_messages.models import Message
from room_messages.permissions import IsSender


def test_message_create(api_client, room_user1, user3):
    api_client.force_authenticate(room_user1.user)
    response = api_client.post('/api/message/', {'text': 'some text', 'room': room_user1.room.id})
    assert response.status_code == status.HTTP_201_CREATED

    msg = Message.objects.all().first()
    assert response.json() == {'id': response.json()['id'], 'text': 'some text', 'room': room_user1.room.id,
                               'sender': room_user1.user.id,
                               'created_at': f'{msg.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}',
                               'updated_at': f'{msg.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}'}

    api_client.force_authenticate(user3)
    response = api_client.post('/api/message/', {'text': 'some text', 'room': room_user1.room.id})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_message_detail(api_client, message_user1):
    api_client.force_authenticate(message_user1.sender)
    response = api_client.put(f'/api/message/{message_user1.id}/', {'text': 'updated text'})
    assert response.status_code == status.HTTP_200_OK

    msg = Message.objects.all().first()
    assert response.json() == {'id': response.json()['id'], 'text': 'updated text', 'room': message_user1.room.id,
                               'sender': message_user1.sender.id,
                               'created_at': f'{msg.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}',
                               'updated_at': f'{msg.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}'}


def test_permissions(rf, message_user1, user2):
    permission = IsSender()

    rf.put(f'/api/message/{message_user1.id}/', {'title': 'updated'})
    rf.user = message_user1.sender
    assert permission.has_object_permission(rf, None, message_user1)

    rf.user = user2
    assert not permission.has_object_permission(rf, None, message_user1)
