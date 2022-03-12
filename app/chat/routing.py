from chat.consumers import ChatConsumer, UserConsumer
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<pk>\d+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/user/$', UserConsumer.as_asgi())
]
