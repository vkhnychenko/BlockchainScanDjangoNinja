from typing import List
from ninja.security import APIKeyQuery

from users.models import User
from users.models import UserBot
from users.schemas import UserBotCreate, UserBotOut, Referral


class ApiKey(APIKeyQuery):
    param_name = "api_key"

    def authenticate(self, request, key):
        try:
            return User.objects.get(api_key=key)
        except User.DoesNotExist:
            pass


def get_or_create_user(data: UserBotCreate) -> UserBotOut:
    user_data = data.dict()
    try:
        user = UserBot.objects.get(id=user_data['id'])
        user.wallets_count = user.wallets.count()
        return user
    except UserBot.DoesNotExist:
        return UserBot.objects.create(**user_data)


def get_referrals(user_id: int) -> List[Referral]:
    return UserBot.objects.filter(referral=user_id).all()
