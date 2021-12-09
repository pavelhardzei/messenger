from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import UserProfile
from users.permissions import IsAdminOrOwner


@pytest.mark.django_db
@patch('rest_framework.views.APIView.check_object_permissions', lambda *args, **kwargs: True)
class TestUsers:

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def user1(self):
        return UserProfile.objects.create_user('test@test1.org', 'test1', 'TEST1', '2000-01-01', 'testing321')

    @pytest.fixture
    def user2(self):
        return UserProfile.objects.create_user('test2@test.org', 'test2', 'TEST2', '2000-01-01', 'testing321')

    def test_signup(self, api_client):
        response = api_client.post(reverse('signup'), {'email': 'test@test.org', 'user_name': 'test',
                                   'full_name': 'TEST', 'date_of_birth': '2000-01-01', 'password': 'testing321'})
        assert response.status_code == status.HTTP_201_CREATED

    def test_signin(self, api_client, user1):
        response = api_client.post(reverse('signin'), {'email': user1.email, 'password': 'testing321'})
        assert response.status_code == status.HTTP_200_OK

    def test_detail(self, api_client, user1, user2):
        api_client.force_authenticate(user1)
        response = api_client.get(reverse('user_detail', kwargs={'pk': 'me'}))
        assert response.status_code == status.HTTP_200_OK

        response = api_client.patch(reverse('user_detail', kwargs={'pk': 'me'}))
        assert response.status_code == status.HTTP_200_OK

        response = api_client.get(reverse('user_detail', kwargs={'pk': user2.pk}))
        assert response.status_code == status.HTTP_200_OK

    def test_pwd(self, api_client, user1):
        api_client.force_authenticate(user1)
        response = api_client.put(reverse('user_change_pwd', kwargs={'pk': 'me'}), {'old_password': 'testing321',
                                  'password': 'testing', 'password_rep': 'testing'})
        assert response.status_code == status.HTTP_200_OK

    def test_permissions(self, rf, user1, user2):
        permission = IsAdminOrOwner()

        rf.delete(reverse('user_detail', kwargs={'pk': user2.pk}))
        rf.user = user1
        assert not permission.has_object_permission(rf, None, user2)
