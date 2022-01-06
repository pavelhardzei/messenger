import factory
from channels.db import database_sync_to_async


class AsyncFactory(factory.django.DjangoModelFactory):
    @classmethod
    @database_sync_to_async
    def _create(cls, model_class, *args, **kwargs):
        return super()._create(model_class, *args, **kwargs)

    @classmethod
    async def create_batch(cls, size, **kwargs):
        return [await cls.create(**kwargs) for _ in range(size)]
