from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404


class TokenAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope['query_params'] = parse_qs(scope['query_string'].decode())
        scope['user'] = await self.get_user(scope['query_params']['token'][0])

        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, token):
        from rest_framework.authtoken.models import Token
        return get_object_or_404(Token, key=token).user
