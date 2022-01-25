from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from django.conf import settings
from web3 import Web3

from telegram_bot import middlewares

bot = Bot(token=settings.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

i18n = middlewares.setup_i18n(dp)
_ = i18n.gettext

w3 = Web3()
