from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/trade/main/', consumers.TransactionConsumer.as_asgi()),
    re_path(r'ws/trade/chart/', consumers.TimeConsumer.as_asgi()),
]