from typing import Tuple, Any, Optional
from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from telegram_bot.utils.server_api import get_lang


class ACLMiddleware(I18nMiddleware):

    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        user = types.User.get_current()
        return await get_lang(user.id) or user.locale
