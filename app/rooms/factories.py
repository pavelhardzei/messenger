import factory
from faker import Faker
from rooms.models import Room, RoomUser
from users.factories import UserFactory

fake = Faker()


class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room

    title = fake.word()
    description = fake.text(30)
    room_type = Room.RoomType.open


class RoomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RoomUser

    room = factory.SubFactory(RoomFactory)
    user = factory.SubFactory(UserFactory)
    role = RoomUser.Role.owner
