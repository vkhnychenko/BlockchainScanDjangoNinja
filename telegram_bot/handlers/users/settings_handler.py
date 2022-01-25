from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hlink
from django.conf import settings

from telegram_bot.loader import dp
from telegram_bot.keyboards import inline_keyboards as inline_kb
from telegram_bot import states
from telegram_bot.utils import server_api
from telegram_bot.utils.exceptions import ServerError
from telegram_bot.handlers.users.message_handlers import render_settings_text


async def render_transactions(call: types.CallbackQuery, transactions: list, index: int):
    await call.message.edit_text(
        render_transactions_text(transactions[index]),
        reply_markup=inline_kb.transactions_kb(len(transactions), index),
        disable_web_page_preview=True
    )


def render_transactions_text(trans: dict):
    wallet = trans["wallet"]
    url = settings.URLS_SCAN[wallet['chain']] + "address/" + wallet['address']
    return f'{hlink(wallet.get("description", wallet["address"]), url)}\n'


@dp.message_handler(text='Настройки', state='*')
async def settings_handler(message: types.Message, state: FSMContext):
    await state.reset_state()
    await message.answer(await render_settings_text(message['db_user']), reply_markup=inline_kb.settings_kb)
    await states.Settings.choice.set()


@dp.callback_query_handler(state=states.Settings.choice)
async def settings_category(call: types.CallbackQuery, state: FSMContext):
    try:
        if call.data == 'last_transactions':
            trans = await server_api.get_transactions(call.message.chat.id)
            await state.update_data(trans=trans, trans_index=0)
            if not trans:
                await call.answer("Не найдено новых транзакций", show_alert=False)
                await call.message.edit_text('Еще нет новых транзакций в боте', reply_markup=inline_kb.back_kb)
            else:
                await call.answer(f"{1} транзакция из {len(trans)}.", show_alert=False)
                await render_transactions(call, trans, 0)
            await states.Settings.transactions.set()
        if call.data == 'filters':
            await call.answer("Фильтры для всех кошельков", show_alert=False)
            await call.message.edit_text('Фильтры для всех кошельков',
                                         reply_markup=inline_kb.filters_kb(call.message['db_user']))
            await states.Settings.filters.set()
        if call.data == 'subscription_info':
            await call.answer("Информация о подписке", show_alert=False)
            await call.message.edit_text('В разработке', reply_markup=inline_kb.back_kb)
            await states.Settings.subscription_info.set()
        if call.data == 'back':
            text = await render_settings_text(call.message['db_user'])
            await call.message.edit_text(text, reply_markup=inline_kb.settings_kb)
    except ServerError:
        await call.message.edit_text('Произошла ошибка соединения с сервером. Попробуйте снова.',
                                     reply_markup=inline_kb.back_kb)


@dp.callback_query_handler(state=states.Settings.transactions)
async def transactions_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get('trans_index')
    trans = data.get('trans')
    if call.data == 'right':
        if index == len(trans) - 1:
            index = 0
        elif index < len(trans) - 1:
            index += 1
        await call.answer(f"{index + 1} транзакция из {len(trans)}.", show_alert=False)
        await render_transactions(call, trans, index)
        await state.update_data(trans_index=index)
    if call.data == 'left':
        if index == 0:
            index = len(trans) - 1
        elif index > 0:
            index -= 1
        await call.answer(f"{index + 1} транзакция из {len(trans)}.", show_alert=False)
        await render_transactions(call, trans, index)
        await state.update_data(trans_index=index)
    if call.data == 'back':
        await state.reset_state()
        await call.message.edit_text(await render_settings_text(call.message['db_user']),
                                     reply_markup=inline_kb.settings_kb)
        await states.Settings.choice.set()


@dp.callback_query_handler(state=states.Settings.subscription_info)
async def subscription_info_handler(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await state.reset_state()
        await call.message.edit_text(await render_settings_text(call.message['db_user']), reply_markup=inline_kb.settings_kb)
        await states.Settings.choice.set()

