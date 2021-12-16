from rest_framework import status
from users.permissions import IsAdminOrOwner


def test_signup(api_client):
    response = api_client.post('/api/user/signup/', {'email': 'test@test.org', 'user_name': 'test',
                               'full_name': 'TEST', 'date_of_birth': '2000-01-01', 'password': 'testing321'})
    assert response.status_code == status.HTTP_201_CREATED


def test_signin(api_client, user1):
    response = api_client.post('/api/user/signin/', {'email': user1.email, 'password': 'testing321'})
    assert response.status_code == status.HTTP_200_OK


def test_detail(api_client, user1, user2):
    api_client.force_authenticate(user1)
    response = api_client.get('/api/user/me/')
    assert response.status_code == status.HTTP_200_OK
    assert set(response.json()) == {'id', 'email', 'user_name', 'full_name', 'date_of_birth', 'date_joined'}

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
