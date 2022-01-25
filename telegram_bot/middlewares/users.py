import logging
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler

from telegram_bot.utils.server_api import get_or_create_user
from telegram_bot.utils.exceptions import ServerError


async def get_db_user(user: types.User, message: types.Message) -> dict:
    try:
        db_user = await get_or_create_user(user)
        if not db_user['is_active']:
            await message.answer('Доступ к боту запрещен. Свяжитесь с администратором.')
            raise CancelHandler()
        return db_user
    except ServerError:
        await message.answer('Произошла ошибка при соединении с сервером. Попробуйте позже')
        logging.error('Server error')
        raise CancelHandler()


class UserMiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data: dict):
        if update.message:
            db_user = await get_db_user(update.message.from_user, update.message)
            update.message['db_user'] = db_user
        elif update.callback_query:
            db_user = await get_db_user(update.callback_query.from_user, update.callback_query.message)
            update.callback_query.message['db_user'] = db_user
        else:
            return
