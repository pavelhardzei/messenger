import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from chat.factories import AsyncRoomFactory, AsyncRoomUserFactory, AsyncUserFactory
from faker import Faker
from messenger_project.asgi import application
from rest_framework.authtoken.models import Token

fake = Faker()


@database_sync_to_async
def get_token(user):
    return Token.objects.get_or_create(user=user)[0].key


@pytest.fixture
async def communicator(request):
    user = await AsyncUserFactory()
    room = await AsyncRoomFactory()
    await AsyncRoomUserFactory(user=user, room=room)

    pk = [0, room.pk]
    yield WebsocketCommunicator(application, f'ws/chat/{pk[request.param == 0]}/?token={await get_token(user)}')
