from unittest.mock import patch

import pytest
from pytest_factoryboy import LazyFixture, register
from rest_framework.test import APIClient
from room_messages.factories import MessageFactory
from rooms.factories import RoomFactory, RoomUserFactory
from users.factories import UserFactory

register(UserFactory, 'user1')
register(UserFactory, 'user2')
register(UserFactory, 'user3')

register(RoomFactory, 'room1')

register(RoomUserFactory, 'room_user1', room=LazyFixture('room1'), user=LazyFixture('user1'))
register(RoomUserFactory, 'room_user2', room=LazyFixture('room1'), user=LazyFixture('user2'))

register(MessageFactory, 'message_user1', room=LazyFixture('room1'), sender=LazyFixture('user1'))


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
