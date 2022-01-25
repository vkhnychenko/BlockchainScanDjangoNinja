from django.core.management.base import BaseCommand
import asyncio
import logging

from telegram_bot import middlewares
from telegram_bot.loader import bot, storage


class Command(BaseCommand):
    help = u'Start bot'

    @staticmethod
    async def on_startup(dp):
        logging.info('start bot')
        print('start bot')
        middlewares.setup(dp)

    @staticmethod
    async def on_shutdown(dp):
        await bot.close()
        await storage.close()

    def handle(self, *args, **kwargs):
        from aiogram import executor
        from telegram_bot.handlers import dp

        executor.start_polling(dp, on_startup=self.on_startup, on_shutdown=self.on_shutdown)
