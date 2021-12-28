import factory
from django.contrib.auth.hashers import make_password
from faker import Faker
from users.models import UserProfile

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    email = factory.Sequence(lambda _: fake.email())
    user_name = factory.Sequence(lambda _: fake.user_name())
    full_name = fake.name()
    date_of_birth = fake.date_of_birth()
    password = make_password('testing321')
