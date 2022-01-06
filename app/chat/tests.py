from unittest.mock import ANY

import pytest
from channels.db import database_sync_to_async
from room_messages.models import Message

pytestmark = pytest.mark.asyncio


@database_sync_to_async
def check_messages(n):
    return Message.objects.count() == n


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('communicator', [0], indirect=True)
async def test_connection(communicator):
    connected, _ = await communicator.connect()
    assert connected

    await communicator.send_json_to({'message': 'hello'})
    response = await communicator.receive_json_from()
    assert response == {'message': 'hello', 'sender': ANY}

    assert await check_messages(1)

    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('communicator', [1], indirect=True)
async def test_room_violation(communicator):
    connected, _ = await communicator.connect()
    assert not connected

    await communicator.disconnect()
