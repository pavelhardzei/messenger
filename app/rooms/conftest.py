from unittest.mock import patch

import pytest
from rest_framework.test import APIClient
from rooms.models import Room, RoomUser
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
        yield UserProfile.objects.create_user('test3@test.org', 'test3', 'TEST3', '2000-01-01', 'testing321')


@pytest.fixture(scope='module')
def user2(django_db_blocker):
    with django_db_blocker.unblock():
        yield UserProfile.objects.create_user('test4@test.org', 'test4', 'TEST4', '2000-01-01', 'testing321')


@pytest.fixture(scope='module')
def user3(django_db_blocker):
    with django_db_blocker.unblock():
        yield UserProfile.objects.create_user('test5@test.org', 'test5', 'TEST5', '2000-01-01', 'testing321')


@pytest.fixture(scope='module')
def room_open(django_db_blocker, user1, user2):
    with django_db_blocker.unblock():
        room = Room.objects.create(title='room1', description='some_info', room_type=Room.RoomType.open)
        RoomUser.objects.create(room=room, user=user1, role=RoomUser.Role.owner)
        RoomUser.objects.create(room=room, user=user2, role=RoomUser.Role.member)
        yield room


@pytest.fixture(scope='module')
def room_closed(django_db_blocker, user1):
    with django_db_blocker.unblock():
        room = Room.objects.create(title='room2', description='some_info', room_type=Room.RoomType.closed)
        RoomUser.objects.create(room=room, user=user1, role=RoomUser.Role.owner)
        yield room
