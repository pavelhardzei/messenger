from base.conftest import api_client, check_object_permissions_mock, enable_db_access_for_all_tests
from pytest_factoryboy import LazyFixture, register
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
