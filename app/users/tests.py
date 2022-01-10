from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework import status
from users.permissions import IsAdminOrOwner


def test_signup(api_client):
    response = api_client.post('/api/user/signup/', {'email': 'test@test.org', 'user_name': 'test',
                               'full_name': 'TEST', 'date_of_birth': '2000-01-01', 'password': 'testing321'})
    assert response.status_code == status.HTTP_201_CREATED


def test_signin(api_client, user1):
    response = api_client.post('/api/user/signin/', {'email': user1.email, 'password': 'testing321'})
    assert response.status_code == status.HTTP_200_OK


def test_list(api_client, user1):
    api_client.force_authenticate(user1)
    response = api_client.get(f'/api/user/?email={user1.email}')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'id': user1.id, 'email': user1.email, 'user_name': user1.user_name,
                                'full_name': user1.full_name, 'date_of_birth': f'{user1.date_of_birth}',
                                'rooms': [], 'date_joined': f'{user1.date_joined}'}]

    response = api_client.get('/api/user/?invalid=some')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_detail(api_client, user1, user2):
    api_client.force_authenticate(user1)
    response = api_client.get('/api/user/me/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'id': user1.id, 'email': user1.email, 'user_name': user1.user_name,
                               'full_name': user1.full_name, 'date_of_birth': f'{user1.date_of_birth}',
                               'rooms': [], 'date_joined': f'{user1.date_joined}'}

    response = api_client.patch('/api/user/me/')
    assert response.status_code == status.HTTP_200_OK

    response = api_client.get(f'/api/user/{user2.pk}/')
    assert response.status_code == status.HTTP_200_OK


def test_pwd(api_client, user1):
    api_client.force_authenticate(user1)
    response = api_client.put('/api/user/change_pwd/me/', {'old_password': 'testing321',
                              'password': 'testing', 'password_rep': 'testing'})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {}


def test_permissions(rf, user1, user2):
    permission = IsAdminOrOwner()

    rf.delete(f'/api/user/{user2.pk}/')
    rf.user = user1
    assert not permission.has_object_permission(rf, None, user2)


def test_get_user_detail_db_calls(api_client, user1, room_user_factory):
    api_client.force_authenticate(user1)

    room_user_factory.create(user=user1)
    with CaptureQueriesContext(connection) as query_context:
        response = api_client.get('/api/user/me/')
    assert response.status_code == status.HTTP_200_OK
    assert len(query_context) == 3

    room_user_factory.create_batch(10, user=user1)
    with CaptureQueriesContext(connection) as query_context:
        response = api_client.get('/api/user/me/')
    assert response.status_code == status.HTTP_200_OK
    assert len(query_context) == 3


def test_get_user_list_db_calls(api_client, user1, room_user_factory):
    api_client.force_authenticate(user1)

    room_user_factory.create_batch(10)
    with CaptureQueriesContext(connection) as query_context:
        response = api_client.get('/api/user/')
    assert response.status_code == status.HTTP_200_OK
    assert len(query_context) == 3

    room_user_factory.create_batch(20)
    with CaptureQueriesContext(connection) as query_context:
        response = api_client.get('/api/user/')
    assert response.status_code == status.HTTP_200_OK
    assert len(query_context) == 3
