from rest_framework import status
from rooms.models import Invitation, RoomUser
from rooms.permissions import IsHigherRole, IsMember, IsOwner
from users.serializers import UserSerializer


def test_create_room(api_client, user1, user2):
    api_client.force_authenticate(user1)
    response = api_client.post('/api/room/', {'title': 'room1', 'description': 'some info',
                                              'room_type': 'closed', 'users': (user2.id, )})
    assert response.status_code == status.HTTP_201_CREATED

    assert response.json() == {'id': response.json()['id'], 'title': 'room1', 'description': 'some info',
                               'room_type': 'closed', 'messages': [],
                               'users': [{'user': UserSerializer(user1).data, 'role': RoomUser.Role.owner},
                                         {'user': UserSerializer(user2).data, 'role': RoomUser.Role.member}]}


def test_list_room(api_client, room_open_user1, room_open_user2):
    api_client.force_authenticate(room_open_user1.user)
    response = api_client.get('/api/room/')

    assert response.status_code == status.HTTP_200_OK

    user1, user2 = room_open_user1.user, room_open_user2.user
    assert response.json() == [{'id': room_open_user1.room.id, 'title': room_open_user1.room.title,
                                'description': room_open_user1.room.description,
                                'room_type': room_open_user1.room.room_type,
                                'messages': [],
                                'users': [{'user': UserSerializer(user1).data, 'role': RoomUser.Role.owner},
                                          {'user': UserSerializer(user2).data, 'role': RoomUser.Role.member}]}]


def test_room_detail(api_client, room_open_user1):
    api_client.force_authenticate(room_open_user1.user)
    response = api_client.get(f'/api/room/{room_open_user1.room.id}/')
    assert response.status_code == status.HTTP_200_OK

    response = api_client.patch(f'/api/room/{room_open_user1.room.id}/', {'title': 'room', 'description': 'new info'})
    assert response.status_code == status.HTTP_200_OK


def test_room_enter_leave(api_client, user3, room_closed, room_open_user1):
    api_client.force_authenticate(user3)
    response = api_client.post('/api/room/enter/', {'room': room_open_user1.room.id})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'id': response.json()['id'], 'room': room_open_user1.room.id, 'user': user3.id,
                               'role': RoomUser.Role.member}

    response = api_client.post('/api/room/leave/', {'room': room_open_user1.room.id})
    assert response.status_code == status.HTTP_200_OK

    response = api_client.post('/api/room/enter/', {'room': room_closed.id})
    assert response.status_code == status.HTTP_403_FORBIDDEN

    api_client.force_authenticate(room_open_user1.user)
    response = api_client.post('/api/room/leave/', {'room': room_open_user1.room.id})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_remove_user(api_client, room_open_user1, room_open_user2):
    api_client.force_authenticate(room_open_user1.user)
    response = api_client.post('/api/room/remove/', {'room': room_open_user1.room.id, 'user': room_open_user2.user.id})
    assert response.status_code == status.HTTP_200_OK


def test_set_role(api_client, room_open_user1, room_open_user2):
    api_client.force_authenticate(room_open_user1.user)
    response = api_client.post('/api/room/setrole/', {'room': room_open_user1.room.id, 'user': room_open_user2.user.id,
                                                      'role': RoomUser.Role.moderator})
    assert response.status_code == status.HTTP_200_OK


def test_invitation(api_client, user3, room_open, room_open_user1, room_closed_user1):
    api_client.force_authenticate(user3)
    response = api_client.post('/api/room/invitation/', {'room': room_open_user1.room.id})
    assert response.status_code == status.HTTP_403_FORBIDDEN

    api_client.force_authenticate(room_open_user1.user)
    response = api_client.post('/api/room/invitation/', {'room': room_closed_user1.room.id})
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = api_client.post('/api/room/invitation/', {'room': room_open_user1.room.id})
    assert response.status_code == status.HTTP_201_CREATED

    inv = Invitation.objects.all().first()
    assert response.json() == {'id': f'{inv.id}', 'room': room_open_user1.room.id,
                               'created': f'{inv.created.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}',
                               'expiration': '1 00:00:00'}

    uuid4 = response.json()['id']
    response = api_client.post(f'/api/room/invitation/{uuid4}/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    api_client.force_authenticate(user3)
    response = api_client.post(f'/api/room/invitation/{uuid4}/')
    assert response.status_code == status.HTTP_200_OK
    assert len(room_open.users.all()) == 2


def test_permissions(rf, room_open_user1, room_open_user2):
    permission = IsMember()

    rf.patch(f'/api/room/{room_open_user1.room.id}/', {'title': 'new'})
    rf.method = 'PATCH'
    rf.user = room_open_user1.user
    assert permission.has_object_permission(rf, None, room_open_user1.room)

    rf.user = room_open_user2.user
    assert not permission.has_object_permission(rf, None, room_open_user2.room)

    permission = IsHigherRole()

    rf.post('/api/room/remove/', {'room': room_open_user1.room.id, 'user': room_open_user2.user.id})
    rf.user = room_open_user1.user
    assert permission.has_object_permission(rf, None, room_open_user2)

    rf.post('/api/room/remove/', {'room': room_open_user1.room.id, 'user': room_open_user1.user.id})
    rf.user = room_open_user2.user
    assert not permission.has_object_permission(rf, None, room_open_user1)

    permission = IsOwner()

    rf.post('/api/room/setrole/', {'room': room_open_user1.room.id, 'user': room_open_user2.user.id,
                                   'role': RoomUser.Role.moderator})
    rf.user = room_open_user1.user
    assert permission.has_object_permission(rf, None, room_open_user2)

    rf.post('/api/room/setrole/', {'room': room_open_user1.room.id, 'user': room_open_user1.user.id,
                                   'role': RoomUser.Role.member})
    rf.user = room_open_user2.user
    assert not permission.has_object_permission(rf, None, room_open_user1)
