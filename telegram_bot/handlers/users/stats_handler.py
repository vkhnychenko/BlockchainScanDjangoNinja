from aiogram import types
from aiogram.dispatcher import FSMContext
from httpx._exceptions import HTTPStatusError
from django.conf import settings
import re
from datetime import datetime
import time

from telegram_bot.utils.stats_wallets import render_stats_wallets, render_normal_tx_text, render_token_tx_text
from telegram_bot.utils.wallet import send_wallets
from telegram_bot.loader import dp, bot, w3
from telegram_bot.keyboards import inline_keyboards as inline_kb
from telegram_bot import states
from telegram_bot.utils.exceptions import ServerError
from telegram_bot.utils.server_api import get_stats_transactions, delete_stats_wallet, get_stats_wallets,\
    add_stats_wallet, update_stats_wallet


async def send_stats_wallets(call: types.CallbackQuery, state: FSMContext, index: int = 0):
    data = await state.get_data()
    wallets = data.get('stats_wallets')
    main_wallet_index = data.get('wallet_id')
    if not wallets:
        wallets = await get_stats_wallets(main_wallet_index)
    if not wallets:
        await bot.answer_callback_query(call.id, "У вас еще нет добавленных кошельков", show_alert=False)
        await call.message.edit_text('У вас еще нет добавленных кошельков',
                                     reply_markup=inline_kb.stats_kb(is_empty=True))
    else:
        await bot.answer_callback_query(call.id, f"{index + 1} кошелек для анализа из {len(wallets)}.", show_alert=False)
        await render_stats_wallets(call, wallets, index)
    await state.update_data(stats_wallets=wallets, stats_wallet_index=index)
    await states.Settings.stats.set()


@dp.callback_query_handler(state=states.Settings.stats)
async def stats_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    wallet_index = data.get('stats_wallet_index')
    wallets = data.get('stats_wallets')
    if call.data == 'add_stats_wallet':
        await call.message.edit_text('Отправьте адрес кошелька для отслеживания')
        await states.Stats.address.set()
    if call.data == 'stats_balance':
        await call.message.answer('Идет обработка, ожидайте...')
        try:
            tx = await get_stats_transactions(wallets[wallet_index]['id'])
            curr = settings.NATIVE_CURRENCY[wallets[wallet_index]["wallet"]["chain"]]
            address = wallets[wallet_index]["address"]
            if tx['normal_input']:
                await call.message.answer(render_normal_tx_text(tx["normal_input"], address, 'input', curr))
            if tx['normal_output']:
                await call.message.answer(render_normal_tx_text(tx["normal_output"], address, 'output', curr))
            if tx['token_input']:
                await call.message.answer(render_token_tx_text(tx["token_input"], address, 'input'))
            if tx['token_output']:
                await call.message.answer(render_token_tx_text(tx["token_output"], address, 'output'))
            if not tx['normal_input'] and not tx['normal_output'] and not tx['token_input'] and not tx['token_output']:
                await call.message.answer('Нет транзакций по указанному кошельку')
        except ServerError:
            await call.message.answer(f'Произошла ошибка соединения с сервером. Попробуйте снова.')
    if call.data == 'delete_stats_wallet':
        try:
            await delete_stats_wallet(wallets[wallet_index]['id'])
            await bot.answer_callback_query(call.id, f'Кошелек: {wallets[wallet_index]["address"]} Успешно удален.',
                                            show_alert=True)
            await state.update_data(stats_wallets=None)
            await send_stats_wallets(call, state, 0)
        except ServerError:
            await bot.answer_callback_query(
                call.id, f'Призошла ошибка при удалении кошелька: {wallets[wallet_index]["address"]}', show_alert=True)
    if call.data == 'edit_timestamp_start':
        await call.message.edit_text('Введите дату в формате "DD-MM-YYYY"', reply_markup=inline_kb.back_kb)
        await states.Stats.start_timestamp.set()
    if call.data == 'edit_timestamp_end':
        await call.message.edit_text('Введите дату в формате "DD-MM-YYYY"', reply_markup=inline_kb.back_kb)
        await states.Stats.end_timestamp.set()
    if call.data == 'right':
        if wallet_index == len(wallets) - 1:
            wallet_index = 0
        elif wallet_index < len(wallets) - 1:
            wallet_index += 1
        await send_stats_wallets(call, state, wallet_index)
    if call.data == 'left':
        if wallet_index == 0:
            wallet_index = len(wallets) - 1
        elif wallet_index > 0:
            wallet_index -= 1
        await send_stats_wallets(call, state, wallet_index)
    if call.data == 'back':
        await send_wallets(call, state, data.get('wallet_index'))


@dp.message_handler(state=states.Stats.address)
async def stats_wallet_name_handler(message: types.Message, state: FSMContext):
    if not w3.isAddress(message.text):
        await message.answer('Неверный формат кошелка. Введите адрес кошелька еще раз.',
                             reply_markup=inline_kb.cancel_kb)
        await states.Stats.address.set()
    else:
        await message.answer(
            f'Введите название для кошелька:\n {message.text}', reply_markup=inline_kb.skip_kb)
        await state.update_data(address=message.text)
        await states.Stats.name.set()


@dp.message_handler(state=states.Stats.name)
async def add_stats_wallet_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data.update({'description': message.text})
    try:
        await add_stats_wallet(data)
        await message.answer(f'Аналитика для {data.get("address")} успешно добавлена.')
        await state.reset_state()
    except HTTPStatusError as e:
        if e.response.status_code == 409:
            await message.answer('Аналитика для указанного адреса уже подключена. Введите другой адрес кошелька.')
            await states.Stats.address.set()
    except ServerError:
        await message.answer(f'Произошла ошибка при добавлении аналитики: {data.get("address")} Попробуйте снова.')
        await state.reset_state()


@dp.callback_query_handler(state=states.Stats.name)
async def stats_wallet_skip_name_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.answer_callback_query(call.id, "Пропуск названия", show_alert=False)
    await call.message.delete()
    try:
        await add_stats_wallet(data)
        await call.message.answer(f'Аналитика для {data.get("address")} успешно добавлена.')
        await state.reset_state()
    except HTTPStatusError as e:
        if e.response.status_code == 409:
            await call.message.answer('Аналитика для указанного адреса уже существует. Введите другой адрес кошелька.')
            await states.Stats.address.set()
    except ServerError:
        await call.message.answer(f'Произошла ошибка при добавлении аналитики: {data.get("address")} Попробуйте снова.')
        await state.reset_state()


@dp.message_handler(state=states.Stats.start_timestamp)
async def start_timestamp_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if re.findall(r'(?<!\d)(?:0?[1-9]|[12][0-9]|3[01])-(?:0?[1-9]|1[0-2])-(?:19[0-9][0-9]|20[0-9][0-9])(?!\d)', message.text):
        await update_stats_wallet(
            data['stats_wallets'][data['stats_wallet_index']]['id'],
            {'start_timestamp': int(time.mktime(datetime.strptime(message.text, "%d-%m-%Y").timetuple()))}
        )
        await message.answer('Дата  начала изменена.')
    else:
        await message.answer('Неверно указана дата. Введите дату в формате "DD-MM-YYYY"')


@dp.message_handler(state=states.Stats.end_timestamp)
async def end_timestamp_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if re.findall(r'(?<!\d)(?:0?[1-9]|[12][0-9]|3[01])-(?:0?[1-9]|1[0-2])-(?:19[0-9][0-9]|20[0-9][0-9])(?!\d)', message.text):
        await update_stats_wallet(
            data['stats_wallets'][data['stats_wallet_index']]['id'],
            {'end_timestamp': int(time.mktime(datetime.strptime(message.text, "%d-%m-%Y").timetuple()))}
        )
        await message.answer('Дата окончания изменена.')
    else:
        await message.answer('Неверно указана дата. Введите дату в формате "DD-MM-YYYY"')


@dp.callback_query_handler(state=states.Stats.start_timestamp)
async def filters_back_handler(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await send_stats_wallets(call, state, 0)


@dp.callback_query_handler(state=states.Stats.end_timestamp)
async def filters_back_handler(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'back':
        await send_stats_wallets(call, state, 0)
