from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from telegram_bot.loader import dp
from telegram_bot.keyboards import reply_keyboards as reply_kb


@dp.message_handler(CommandStart(), state='*')
async def bot_start(message: types.Message):
    await message.answer(f'Приветствую {message.from_user.first_name}', reply_markup=reply_kb.start_kb)
