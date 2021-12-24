from unittest.mock import patch

import pytest
from pytest_factoryboy import LazyFixture, register
from rest_framework.test import APIClient
from rooms.factories import RoomFactory, RoomUserFactory
from rooms.models import Room, RoomUser
from users.factories import UserFactory

register(UserFactory, 'user1')
register(UserFactory, 'user2')
register(UserFactory, 'user3')

register(RoomFactory, 'room_open', room_type=Room.RoomType.open)
register(RoomFactory, 'room_closed', room_type=Room.RoomType.closed)

register(RoomUserFactory, 'room_open_user1', room=LazyFixture('room_open'), user=LazyFixture('user1'))
register(RoomUserFactory, 'room_closed_user1', room=LazyFixture('room_closed'), user=LazyFixture('user1'))
register(RoomUserFactory, 'room_open_user2', room=LazyFixture('room_open'), user=LazyFixture('user2'),
         role=RoomUser.Role.member)


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
