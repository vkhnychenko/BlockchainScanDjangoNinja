from django.urls import re_path
from .consumers import WalletConsumer

websockets_urlpatterns = [
    re_path(r'ws/balances/(?P<user_id>\d+)', WalletConsumer.as_asgi())
]