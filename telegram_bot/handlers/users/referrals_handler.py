from aiogram import types

from telegram_bot.loader import dp, bot
import telegram_bot.keyboards.inline_keyboards as inline_kb
from telegram_bot import states
from telegram_bot.utils.server_api import get_referrals
from telegram_bot.utils.exceptions import ServerError


async def render_text(message: types.Message):
    bot_username = (await message.bot.get_me()).username
    bot_link = f'https://t.me/{bot_username}?start={message.from_user.id}'
    text = f'Делитесь ссылкой на бота и получайте ' \
           f'{message["db_user"]["referral_bonus"]}% от трат приглашенных пользователей!\n' \
           f'Ссылка для приглашения: {bot_link}'
    return text


@dp.message_handler(text='Партнерская программа', state='*')
async def partner_program(message: types.Message):
    await message.answer(await render_text(message), reply_markup=inline_kb.referrals_kb)
    await states.Referral.info.set()


@dp.callback_query_handler(state=states.Referral.info)
async def referrals_info(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    if call.data == 'referrals':
        try:
            referrals = await get_referrals(call.from_user.id)
            if not referrals:
                await call.message.edit_text('У вас еще нет приглашенных пользователей.',
                                             reply_markup=inline_kb.back_kb)
            else:
                text = 'Список приглашенных пользователей:\n'
                for obj in referrals:
                    chat = await bot.get_chat(obj['id'])
                    user_link = chat.get_mention(as_html=True)
                    text += f'{user_link}\n'
                await call.message.edit_text(text, reply_markup=inline_kb.back_kb)
        except ServerError:
            await call.message.answer('Произошла ошибка соединения с сервером. Попробуйте снова.')
    if call.data == 'referral_balance':
        if not call.message["db_user"].get('referral_balance'):
            await call.message.edit_text('У вас еще нет средств доступных для вывода', reply_markup=inline_kb.back_kb)
        else:
            await call.message.edit_text('Ваш партнерский баланс: {call["db_user"]["referral_balance"]} USD',
                                         reply_markup=inline_kb.back_kb)
    if call.data == 'back':
        await call.message.edit_text(await render_text(call.message), reply_markup=inline_kb.referrals_kb)
        await states.Referral.info.set()
