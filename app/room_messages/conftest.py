from base.conftest import api_client, check_object_permissions_mock, enable_db_access_for_all_tests
from pytest_factoryboy import LazyFixture, register
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
