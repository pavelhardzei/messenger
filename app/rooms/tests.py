from rest_framework import status
from rooms.models import RoomUser
from rooms.permissions import IsHigherRole, IsMember, IsOwner


def test_create_room(api_client, user1, user2):
    api_client.force_authenticate(user1)
    response = api_client.post('/api/room/', {'title': 'room1', 'description': 'some info',
                                              'room_type': 'closed', 'users': (user2.id, )})
    assert response.status_code == status.HTTP_201_CREATED
    assert set(response.json()) == {'id', 'title', 'description', 'room_type', 'users'}


def test_list_room(api_client, user1, room_open):
    api_client.force_authenticate(user1)
    response = api_client.get('/api/room/')

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_room_detail(api_client, user1, room_open):
    api_client.force_authenticate(user1)
    response = api_client.get(f'/api/room/{room_open.id}/')
    assert response.status_code == status.HTTP_200_OK

    response = api_client.patch(f'/api/room/{room_open.id}/', {'title': 'room', 'description': 'new info'})
    assert response.status_code == status.HTTP_200_OK


def test_room_enter_leave(api_client, user1, user3, room_open, room_closed):
    api_client.force_authenticate(user3)
    response = api_client.post('/api/room/enter/', {'room': room_open.id})
    assert response.status_code == status.HTTP_200_OK
    assert set(response.json()) == {'id', 'room', 'user', 'role'}

    response = api_client.post('/api/room/leave/', {'room': room_open.id})
    assert response.status_code == status.HTTP_200_OK

    response = api_client.post('/api/room/enter/', {'room': room_closed.id})
    assert response.status_code == status.HTTP_403_FORBIDDEN

    api_client.force_authenticate(user1)
    response = api_client.post('/api/room/leave/', {'room': room_open.id})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_remove_user(api_client, user1, user2, room_open):
    api_client.force_authenticate(user1)
    response = api_client.post('/api/room/remove/', {'room': room_open.id, 'user': user2.id})
    assert response.status_code == status.HTTP_200_OK


def test_set_role(api_client, user1, user2, room_open):
    api_client.force_authenticate(user1)
    response = api_client.post('/api/room/remove/', {'room': room_open.id, 'user': user2.id,
                                                     'role': RoomUser.Role.moderator})
    assert response.status_code == status.HTTP_200_OK


def test_invitation(api_client, user1, user3, room_open, room_closed):
    api_client.force_authenticate(user3)
    response = api_client.post('/api/room/invitation/', {'room': room_open.id})
    assert response.status_code == status.HTTP_403_FORBIDDEN

    api_client.force_authenticate(user1)
    response = api_client.post('/api/room/invitation/', {'room': room_closed.id})
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = api_client.post('/api/room/invitation/', {'room': room_open.id})
    assert response.status_code == status.HTTP_201_CREATED
    assert set(response.json()) == {'id', 'room', 'created', 'expiration'}

    uuid4 = response.json()['id']
    response = api_client.post(f'/api/room/invitation/{uuid4}/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    api_client.force_authenticate(user3)
    response = api_client.post(f'/api/room/invitation/{uuid4}/')
    assert response.status_code == status.HTTP_200_OK
    assert len(room_open.users.all()) == 3


def test_permissions(rf, user1, user2, room_open):
    permission = IsMember()

    rf.patch(f'/api/room/{room_open.id}/', {'title': 'new'})
    rf.method = 'PATCH'
    rf.user = user1
    assert permission.has_object_permission(rf, None, room_open)

    rf.user = user2
    assert not permission.has_object_permission(rf, None, room_open)

    permission = IsHigherRole()

    rf.post('/api/room/remove/', {'room': room_open.id, 'user': user2.id})
    rf.user = user1
    assert permission.has_object_permission(rf, None, RoomUser.objects.get(room=room_open.id, user=user2.id))

    rf.post('/api/room/remove/', {'room': room_open.id, 'user': user1.id})
    rf.user = user2
    assert not permission.has_object_permission(rf, None, RoomUser.objects.get(room=room_open.id, user=user1.id))

    permission = IsOwner()

    rf.post('/api/room/setrole/', {'room': room_open.id, 'user': user2.id, 'role': RoomUser.Role.moderator})
    rf.user = user1
    assert permission.has_object_permission(rf, None, RoomUser.objects.get(room=room_open.id, user=user2.id))

    rf.post('/api/room/setrole/', {'room': room_open.id, 'user': user1.id, 'role': RoomUser.Role.member})
    rf.user = user2
    assert not permission.has_object_permission(rf, None, RoomUser.objects.get(room=room_open.id, user=user1.id))
