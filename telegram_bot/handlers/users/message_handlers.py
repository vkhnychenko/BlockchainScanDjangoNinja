from aiogram import types
from aiogram.dispatcher import FSMContext
from django.conf import settings

from telegram_bot.loader import dp, bot
from telegram_bot import states


async def render_settings_text(user_db: dict) -> str:
    if user_db['subscription_is_active']:
        text = f'Подписка активна до: {user_db["date_end_subscription"]}\n'
    else:
        text = f'Подписка не активна\n'
    text += f'Добавлено кошельков: {user_db["wallets_count"]}\n'
    text += f'Лимит кошельков {user_db["available_wallets_count"]}\n' if user_db["available_wallets_count"] else ''
    text += f'Валюта для пересчета стоимости: USD'
    return text


@dp.message_handler(text='Обратная связь', state='*')
async def feedback_handler(message: types.Message, state: FSMContext):
    await state.reset_state()
    await message.answer('Напишите ваш вопрос или предложение.')
    await states.Feedback.message.set()


@dp.message_handler(state=states.Feedback.message)
async def message_handler(message: types.Message, state: FSMContext):
    chat = await bot.get_chat(message.from_user.id)
    user_link = chat.get_mention(as_html=True)
    for admin in settings.ADMINS:
        await bot.send_message(admin, f'Пришло сообщение от пользователя: {user_link}\n'
                                      f'{message.text}')
    await message.answer('Ваше сообщение отправлено. Вам ответят в ближайшее время.')
    await state.reset_state()


@dp.message_handler(text='Поддержать проект', state='*')
async def support_handler(message: types.Message):
    await message.answer(
        'Для поддежрки данного проекта вы можете перечислить финансы на счет кошелька в сетях Ethereum, BSC, Polygon:\n\n'
        f'<b>{settings.DONATE_WALLET}</b>\n\n')
        # f'Ethereum: {render_link(None, "0xEe7cABe78FBd21BBBD7649234E0002A86Aa1fF8d", "eth", "address")}\n'
        # f'Binance Smart Chain: {render_link(None, "0xEe7cABe78FBd21BBBD7649234E0002A86Aa1fF8d", "bsc", "address")}\n'
        # f'Polygon: {render_link(None, "0xEe7cABe78FBd21BBBD7649234E0002A86Aa1fF8d", "polygon", "address")}')


@dp.message_handler(text='Язык', state='*')
async def support_handler(message: types.Message, state: FSMContext):
    await state.reset_state()
    await message.answer('Поддержка других языков. Находится в разработке')
