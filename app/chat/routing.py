from chat import consumers
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<pk>\d+)/$', consumers.ChatConsumer.as_asgi()),
]
