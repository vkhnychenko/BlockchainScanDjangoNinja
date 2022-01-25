from typing import List
from ninja import Router
from ninja.errors import HttpError

from . import services
from .schemas import UserBotOut, UserBotCreate, Referral, UserBotUpdate
from .models import UserBot

user_router = Router(tags=['user'])


@user_router.post('/bot', response=UserBotOut)
def get_or_create_user(request, user_data: UserBotCreate):
    return services.get_or_create_user(user_data)


@user_router.post('/bot/{pk}')
def update_user(request, pk: int, data: UserBotUpdate):
    try:
        user = UserBot.objects.get(pk=pk)
        user.native_transfer = data.native_transfer if data.native_transfer is not None else user.native_transfer
        user.token_transfer = data.token_transfer if data.token_transfer is not None else user.token_transfer
        user.nft_transfer = data.nft_transfer if data.nft_transfer is not None else user.nft_transfer
        user.limit_native = data.limit_native if data.limit_native is not None and data.limit_native >= 0 else user.limit_native
        user.limit_tokens = data.limit_tokens if data.limit_tokens is not None and data.limit_tokens >= 0 else user.limit_tokens
        user.limit_currency = data.limit_currency if data.limit_currency is not None and data.limit_currency >= 0 else user.limit_currency
        user.save()
        return {'status': 'ok'}
    except UserBot.DoesNotExist:
        raise HttpError(404, "Not found")


@user_router.get('/referrals', response=List[Referral])
def get_referrals(request, bot_user_id: int = None):
    return services.get_referrals(bot_user_id)
