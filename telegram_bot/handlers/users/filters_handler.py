from aiogram import types
from aiogram.dispatcher import FSMContext

from telegram_bot.handlers.users.wallets_handler import send_wallets
from telegram_bot.loader import dp
from telegram_bot.keyboards import inline_keyboards as inline_kb
from telegram_bot import states
from telegram_bot.handlers.users.message_handlers import render_settings_text
from telegram_bot.utils.server_api import update_wallet, update_user


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


@dp.callback_query_handler(state=states.Settings.filters)
async def filters_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    curr_data = data['wallets'][data['wallet_index']] if data.get('wallets') else call.message['db_user']
    if call.data == 'native_transfer':
        curr_data['native_transfer'] = not curr_data['native_transfer']
        if data.get('wallets'):
            await update_wallet(curr_data['id'], {'native_transfer': curr_data['native_transfer']})
            data['wallets'][data['wallet_index']]['native_transfer'] = curr_data['native_transfer']
            await state.update_data(wallets=data['wallets'])
        else:
            await update_user(curr_data['id'], {'native_transfer': curr_data['native_transfer']})
        await call.message.edit_reply_markup(inline_kb.filters_kb(curr_data))
    if call.data == 'token_transfer':
        curr_data['token_transfer'] = not curr_data['token_transfer']
        if data.get('wallets'):
            await update_wallet(curr_data['id'], {'token_transfer': curr_data['token_transfer']})
            data['wallets'][data['wallet_index']]['token_transfer'] = curr_data['token_transfer']
            await state.update_data(wallets=data['wallets'])
        else:
            await update_user(curr_data['id'], {'token_transfer': curr_data['token_transfer']})
        await call.message.edit_reply_markup(inline_kb.filters_kb(curr_data))
    if call.data == 'nft_transfer':
        curr_data['nft_transfer'] = not curr_data['nft_transfer']
        if data.get('wallets'):
            await update_wallet(curr_data['id'], {'nft_transfer': curr_data['nft_transfer']})
            data['wallets'][data['wallet_index']]['nft_transfer'] = curr_data['nft_transfer']
            await state.update_data(wallets=data['wallets'])
        else:
            await update_user(curr_data['id'], {'nft_transfer': curr_data['nft_transfer']})
        await call.message.edit_reply_markup(inline_kb.filters_kb(curr_data))
    if call.data == 'limit_native':
        await call.message.edit_text('Введите лимит основной валюты. Для дробных числе используйте "."',
                                     reply_markup=inline_kb.back_kb)
        await states.Filter.limit_native.set()
    if call.data == 'limit_tokens':
        await call.message.edit_text('Введите лимит токенов. Для дробных числе используйте "."',
                                     reply_markup=inline_kb.back_kb)
        await states.Filter.limit_tokens.set()
    if call.data == 'limit_currency':
        #todo fix currency
        await call.message.edit_text('Введите лимит USD. Для дробных числе используйте "."',
                                     reply_markup=inline_kb.back_kb)
        await states.Filter.limit_currency.set()
    if call.data == 'back':
        if data.get('wallets'):
            await send_wallets(call, state, data.get('wallet_index'))
        else:
            await state.reset_state()
            await call.message.edit_text(await render_settings_text(curr_data), reply_markup=inline_kb.settings_kb)
            await states.Settings.choice.set()


@dp.message_handler(state=states.Filter.limit_native)
async def filters_limit_native_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if isfloat(message.text):
        if data.get('wallets'):
            await update_wallet(data['wallets'][data['wallet_index']]['id'], {'limit_native': message.text})
        else:
            await update_user(message['db_user']['id'], {'limit_native': message.text})
        await message.answer('Обновлено успешно')
    else:
        await message.answer('Введите число, которое будет больше или равно 0.')


@dp.message_handler(state=states.Filter.limit_tokens)
async def filters_limit_tokens_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if isfloat(message.text):
        if data.get('wallets'):
            await update_wallet(data['wallets'][data['wallet_index']]['id'], {'limit_tokens': message.text})
        else:
            await update_user(message['db_user']['id'], {'limit_tokens': message.text})
        await message.answer('Обновлено успешно')
    else:
        await message.answer('Введите число, которое будет больше или равно 0.')


@dp.message_handler(state=states.Filter.limit_currency)
async def filters_limit_currency_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if isfloat(message.text):
        if data.get('wallets'):
            await update_wallet(data['wallets'][data['wallet_index']]['id'], {'limit_currency': message.text})
        else:
            await update_user(message['db_user']['id'], {'limit_currency': message.text})
        await message.answer('Обновлено успешно')
    else:
        await message.answer('Введите число, которое будет больше или равно 0.')


@dp.callback_query_handler(state=states.Filter.limit_native)
async def filters_back_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == 'back':
        if data.get('wallets'):
            await call.message.edit_text(
                'Фильтры', reply_markup=inline_kb.filters_kb(data['wallets'][data['wallet_index']])
            )
        else:
            await call.message.edit_text(
                'Фильтры', reply_markup=inline_kb.filters_kb(call.message['db_user'])
            )
        await states.Settings.filters.set()


@dp.callback_query_handler(state=states.Filter.limit_tokens)
async def filters_back_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == 'back':
        if data.get('wallets'):
            await call.message.edit_text(
                'Фильтры', reply_markup=inline_kb.filters_kb(data['wallets'][data['wallet_index']])
            )
        else:
            await call.message.edit_text(
                'Фильтры', reply_markup=inline_kb.filters_kb(call.message['db_user'])
            )
        await states.Settings.filters.set()


@dp.callback_query_handler(state=states.Filter.limit_currency)
async def filters_back_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == 'back':
        if data.get('wallets'):
            await call.message.edit_text(
                'Фильтры', reply_markup=inline_kb.filters_kb(data['wallets'][data['wallet_index']])
            )
        else:
            await call.message.edit_text(
                'Фильтры', reply_markup=inline_kb.filters_kb(call.message['db_user'])
            )
        await states.Settings.filters.set()
