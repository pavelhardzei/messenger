from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework import status
from rooms.models import Invitation, RoomUser
from rooms.permissions import IsHigherRole, IsMember, IsOwner


def test_create_room(api_client, user1, user2):
    api_client.force_authenticate(user1)
    response = api_client.post('/api/room/', {'title': 'room1', 'description': 'some info',
                                              'room_type': 'closed', 'users': (user2.id,)})
    assert response.status_code == status.HTTP_201_CREATED

    assert response.json() == {'id': 1, 'title': 'room1', 'description': 'some info', 'room_type': 'closed',
                               'users': [
                                   {'user': {'id': user1.id, 'email': user1.email, 'user_name': user1.user_name,
                                             'full_name': user1.full_name, 'date_of_birth': f'{user1.date_of_birth}',
                                             'date_joined': f'{user1.date_joined}'}, 'role': RoomUser.Role.owner},
                                   {'user': {'id': user2.id, 'email': user2.email, 'user_name': user2.user_name,
                                             'full_name': user2.full_name, 'date_of_birth': f'{user2.date_of_birth}',
                                             'date_joined': f'{user2.date_joined}'}, 'role': RoomUser.Role.member}
                               ]}


def test_list_room(api_client, room_open_user1, room_open_user2):
    api_client.force_authenticate(room_open_user1.user)
    response = api_client.get('/api/room/')

    assert response.status_code == status.HTTP_200_OK

    user1, user2 = room_open_user1.user, room_open_user2.user
    assert response.json() == [{'id': room_open_user1.room.id, 'title': room_open_user1.room.title,
                                'description': room_open_user1.room.description,
                                'room_type': room_open_user1.room.room_type,
                                'users': [
                                    {'user': {'id': user1.id, 'email': user1.email, 'user_name': user1.user_name,
                                              'full_name': user1.full_name, 'date_of_birth': f'{user1.date_of_birth}',
                                              'date_joined': f'{user1.date_joined}'}, 'role': RoomUser.Role.owner},
                                    {'user': {'id': user2.id, 'email': user2.email, 'user_name': user2.user_name,
                                              'full_name': user2.full_name, 'date_of_birth': f'{user2.date_of_birth}',
                                              'date_joined': f'{user2.date_joined}'}, 'role': RoomUser.Role.member}
                                ]}]


def test_room_detail(api_client, room_open_user1):
    api_client.force_authenticate(room_open_user1.user)
    response = api_client.get(f'/api/room/{room_open_user1.room.id}/')
    assert response.status_code == status.HTTP_200_OK


def test_room_update(api_client, room_open_user1):
    api_client.force_authenticate(room_open_user1.user)
    response = api_client.patch(f'/api/room/{room_open_user1.room.id}/', {'title': 'room', 'description': 'new info'})
    assert response.status_code == status.HTTP_200_OK


def test_room_enter_leave(api_client, user3, room_closed, room_open_user1):
    api_client.force_authenticate(user3)
    response = api_client.put(f'/api/room/{room_open_user1.room.id}/enter/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'id': response.json()['id'], 'room': room_open_user1.room.id, 'user': user3.id,
                               'role': RoomUser.Role.member}

    response = api_client.post(f'/api/room/{room_open_user1.room.id}/leave/')
    assert response.status_code == status.HTTP_200_OK

    response = api_client.put(f'/api/room/{room_closed.id}/enter/')
    assert response.status_code == status.HTTP_403_FORBIDDEN

    api_client.force_authenticate(room_open_user1.user)
    response = api_client.post(f'/api/room/{room_open_user1.room.id}/leave/')
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_remove_user(api_client, room_open_user1, room_open_user2):
    api_client.force_authenticate(room_open_user1.user)
    response = api_client.delete(f'/api/room/{room_open_user1.room.id}/user/{room_open_user2.user.id}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_set_role(api_client, room_open_user1, room_open_user2):
    api_client.force_authenticate(room_open_user1.user)
    response = api_client.post(f'/api/room/{room_open_user1.room.id}/user/{room_open_user2.user.id}/role/',
                               {'role': RoomUser.Role.moderator})
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


def test_get_room_detail_db_calls(api_client, user1, room_open_user1):
    api_client.force_authenticate(user1)

    with CaptureQueriesContext(connection) as query_context:
        response = api_client.get(f'/api/room/{room_open_user1.room.id}/')
    assert response.status_code == status.HTTP_200_OK
    assert len(query_context) == 3


def test_get_room_list_db_calls(api_client, user1, room_user_factory):
    api_client.force_authenticate(user1)

    room_user_factory.create_batch(10, user=user1)
    with CaptureQueriesContext(connection) as query_context:
        response = api_client.get('/api/room/')
    assert response.status_code == status.HTTP_200_OK
    assert len(query_context) == 3

    room_user_factory.create_batch(20, user=user1)
    with CaptureQueriesContext(connection) as query_context:
        response = api_client.get('/api/room/')
    assert response.status_code == status.HTTP_200_OK
    assert len(query_context) == 3
