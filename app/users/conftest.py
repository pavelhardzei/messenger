from unittest.mock import patch

import pytest
from rest_framework.test import APIClient
from users.models import UserProfile


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(autouse=True)
def check_object_permissions_mock():
    with patch('rest_framework.views.APIView.check_object_permissions'):
        yield True


@pytest.fixture(scope='module')
def api_client(django_db_blocker):
    with django_db_blocker.unblock():
        yield APIClient()


@pytest.fixture(scope='module')
def user1(django_db_blocker):
    with django_db_blocker.unblock():
        yield UserProfile.objects.create_user('test@test1.org', 'test1', 'TEST1', '2000-01-01', 'testing321')


@pytest.fixture(scope='module')
def user2(django_db_blocker):
    with django_db_blocker.unblock():
        yield UserProfile.objects.create_user('test2@test.org', 'test2', 'TEST2', '2000-01-01', 'testing321')
