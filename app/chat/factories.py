from base.factories import AsyncFactory
from rooms.factories import RoomFactory, RoomUserFactory
from users.factories import UserFactory


class AsyncUserFactory(UserFactory, AsyncFactory):
    pass


class AsyncRoomFactory(RoomFactory, AsyncFactory):
    pass


class AsyncRoomUserFactory(RoomUserFactory, AsyncFactory):
    pass
