from django.urls import reverse
from rest_framework import status
from users.permissions import IsAdminOrOwner


def test_signup(api_client):
    response = api_client.post(reverse('signup'), {'email': 'test@test.org', 'user_name': 'test',
                               'full_name': 'TEST', 'date_of_birth': '2000-01-01', 'password': 'testing321'})
    assert response.status_code == status.HTTP_201_CREATED


def test_signin(api_client, user1):
    response = api_client.post(reverse('signin'), {'email': user1.email, 'password': 'testing321'})
    assert response.status_code == status.HTTP_200_OK


def test_detail(api_client, user1, user2):
    api_client.force_authenticate(user1)
    response = api_client.get(reverse('user_detail', kwargs={'pk': 'me'}))
    assert response.status_code == status.HTTP_200_OK

    response = api_client.patch(reverse('user_detail', kwargs={'pk': 'me'}))
    assert response.status_code == status.HTTP_200_OK

    response = api_client.get(reverse('user_detail', kwargs={'pk': user2.pk}))
    assert response.status_code == status.HTTP_200_OK


def test_pwd(api_client, user1):
    api_client.force_authenticate(user1)
    response = api_client.put(reverse('user_change_pwd', kwargs={'pk': 'me'}), {'old_password': 'testing321',
                              'password': 'testing', 'password_rep': 'testing'})
    assert response.status_code == status.HTTP_200_OK


def test_permissions(rf, user1, user2):
    permission = IsAdminOrOwner()

    rf.delete(reverse('user_detail', kwargs={'pk': user2.pk}))
    rf.user = user1
    assert not permission.has_object_permission(rf, None, user2)
