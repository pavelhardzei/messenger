import factory
from faker import Faker
from room_messages.models import Message
from rooms.factories import RoomFactory
from users.factories import UserFactory

fake = Faker()


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    text = fake.text(30)
    room = factory.SubFactory(RoomFactory)
    sender = factory.SubFactory(UserFactory)
