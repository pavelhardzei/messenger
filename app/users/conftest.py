from base.conftest import api_client, check_object_permissions_mock, enable_db_access_for_all_tests
from pytest_factoryboy import register
from rooms.factories import RoomUserFactory
from users.factories import UserFactory

register(UserFactory, 'user1')
register(UserFactory, 'user2')

register(RoomUserFactory)
