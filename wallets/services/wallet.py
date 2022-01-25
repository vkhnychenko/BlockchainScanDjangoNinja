import time
from typing import List
import ciso8601
from ninja.errors import HttpError
from users.models import UserBot
from ..models import Wallet
from ..schemas import WalletCreate, WalletOut


def get_parse_timestamp(datetime: str) -> int:
    return int(time.mktime(ciso8601.parse_datetime(str(datetime)).timetuple()))


def get_user(user_id: int) -> UserBot:
    try:
        return UserBot.objects.get(id=user_id)
    except UserBot.DoesNotExist:
        raise HttpError(404, "User not found")


def get_wallet(address: str, chain: str, user: UserBot) -> Wallet:
    try:
        return Wallet.objects.get(address=address, chain=chain, user=user)
    except Wallet.DoesNotExist:
        raise HttpError(404, "Wallet not found")


def get_wallets(user_id: int) -> List[WalletOut]:
    user = get_user(user_id)
    return Wallet.objects.select_related('user').filter(user=user)


def add_wallet(data: WalletCreate) -> WalletOut:
    user = get_user(data.user_id)
    try:
        Wallet.objects.get(address=data.address, chain=data.chain, user=user)
        raise HttpError(409, "The address with the selected network has already been added")
    except Wallet.DoesNotExist:
        dict_data = data.dict()
        del dict_data['user_id']
        return Wallet.objects.create(user=user, **dict_data)
