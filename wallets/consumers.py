import json
from channels.generic.websocket import WebsocketConsumer

from .services.balance import get_balances


class WalletConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        user_id = self.scope['url_route']['kwargs']['user_id']
        balances = get_balances(user_id)
        for balance in balances:
            self.send(text_data=json.dumps(balance))
        self.close(code=1000)
