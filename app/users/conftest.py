from unittest.mock import patch

import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient
from users.factories import UserFactory

register(UserFactory, 'user1')
register(UserFactory, 'user2')


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
