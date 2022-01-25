from aiogram import types
from aiogram.dispatcher import FSMContext
from httpx._exceptions import HTTPStatusError

from telegram_bot.handlers.users.stats_handler import send_stats_wallets
from telegram_bot.loader import dp, bot, w3
from telegram_bot.keyboards import inline_keyboards as inline_kb
from telegram_bot import states
from telegram_bot.utils.server_api import delete_wallet, update_wallet, get_wallets
from telegram_bot.utils.exceptions import ServerError
from telegram_bot.utils.wallet import send_wallets, render_wallets_text


@dp.message_handler(text='Кошельки', state='*')
async def wallets_handler(message: types.Message, state: FSMContext):
    wallets = await get_wallets(message.chat.id)
    if not wallets:
        await message.answer('У вас еще нет добавленных кошельков.',
                             reply_markup=inline_kb.wallets_kb(0, is_empty=True))
    else:
        await message.answer(render_wallets_text(wallets[0]), disable_web_page_preview=True,
                             reply_markup=inline_kb.wallets_kb(len(wallets), 0,
                                                               show_balance=wallets[0]['show_balance']))
    await state.update_data(wallets=wallets, wallet_index=0)
    await states.Settings.wallets.set()


@dp.callback_query_handler(state=states.Settings.wallets)
async def wallets_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    wallet_index = data.get('wallet_index')
    wallets = data.get('wallets')

    if call.data == 'add_wallet':
        if call.message['db_user']['wallets_count'] == call.message['db_user']['available_wallets_count']:
            text = f'Вы не можете добавить больше <b>{call.message["db_user"]["available_wallets_count"]}</b> кошельков.' \
                   'Оформите подписку для отключения лимита на количество кошельков.'
            await call.message.edit_text(text, reply_markup=inline_kb.subscription_kb)
            await states.Settings.choice.set()
        else:
            await call.message.edit_text('Выберите сеть добавляемого кошелька:', reply_markup=inline_kb.chain_kb)
            await states.Wallet.chain.set()

    if call.data == 'right':
        if wallet_index == len(wallets) - 1:
            wallet_index = 0
        elif wallet_index < len(wallets) - 1:
            wallet_index += 1
        await send_wallets(call, state, wallet_index)

    if call.data == 'left':
        if wallet_index == 0:
            wallet_index = len(wallets) - 1
        elif wallet_index > 0:
            wallet_index -= 1
        await send_wallets(call, state, wallet_index)

    if call.data == 'delete':
        try:
            await delete_wallet(wallets[wallet_index]['id'])
            await bot.answer_callback_query(call.id, f'Кошелек: {wallets[wallet_index]["address"]} Успешно удален.',
                                            show_alert=True)
            await state.update_data(wallets=None)
            await send_wallets(call, state, 0)
        except ServerError:
            await bot.answer_callback_query(
                call.id, f'Призошла ошибка при удалении кошелька: {wallets[wallet_index]["address"]}', show_alert=True)

    if call.data == 'filters':
        await bot.answer_callback_query(call.id, f'Фильтры для кошелька: {wallets[wallet_index]["address"]}',
                                        show_alert=False)
        await call.message.edit_text(f'Фильтры для кошелька: {wallets[wallet_index]["address"]}',
                                     reply_markup=inline_kb.filters_kb(wallets[wallet_index]))
        await states.Settings.filters.set()

    if call.data == 'stats':
        await state.update_data(wallet_id=wallets[wallet_index]['id'])
        await send_stats_wallets(call, state, 0)

    if call.data == 'view_list':
        kb = inline_kb.wallet_list_kb(wallets)
        await call.message.edit_text('Список кошельков', reply_markup=kb)
        await states.Settings.view_list.set()

    if call.data == 'change_name':
        await call.message.edit_text('Пришлите новое описание для кошелька.', reply_markup=inline_kb.back_kb)
        await states.Settings.change_name.set()

    if call.data == 'show_balance':
        wallets[wallet_index]['show_balance'] = not wallets[wallet_index]['show_balance']
        await update_wallet(wallets[wallet_index]['id'], {'show_balance': wallets[wallet_index]['show_balance']})
        await state.update_data(wallets=wallets)
        await send_wallets(call, state, wallet_index)

    # if call.data == 'back':
    #     await state.reset_state()
    #     await call.message.edit_text(await render_settings_text(call.message['db_user']), reply_markup=inline_kb.settings_kb)
    #     await states.Settings.choice.set()


@dp.callback_query_handler(state=states.Wallet.chain)
async def choice_chain(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        f'Отправьте адрес кошелька {call.data.upper()}, который вы хотите добавить для отслеживания.',
        reply_markup=inline_kb.cancel_kb
    )
    await state.update_data(chain=call.data)
    await states.Wallet.address.set()


@dp.message_handler(state=states.Wallet.address)
async def enter_address(message: types.Message, state: FSMContext):
    if not w3.isAddress(message.text):
        await message.answer('Неверный формат кошелка. Введите адрес кошелька еще раз.',
                             reply_markup=inline_kb.cancel_kb)
        await states.Wallet.address.set()
    else:
        await message.answer(
            'Введите название для кошелька:\n'
            f'{message.text}',
            reply_markup=inline_kb.skip_kb
        )
        await state.update_data(address=message.text)
        await states.Wallet.name.set()


@dp.message_handler(state=states.Wallet.name)
async def add_wallet(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data.update({
        'user_id': message.from_user.id,
        'description': message.text
    })
    try:
        await add_wallet(data)
        await message.answer(f'Кошелек {data.get("address")} успешно добавлен.')
        await state.reset_state()
    except HTTPStatusError as e:
        if e.response.status_code == 409:
            await message.answer('Адрес в указаной сети уже существует. Введите другой адрес кошелька.')
            await states.Wallet.address.set()
    except ServerError:
        await message.answer(f'Произошла ошибка при добавлении кошелька: {data.get("address")} Попробуйте снова.')


@dp.callback_query_handler(state=states.Wallet.name)
async def skip_name(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data.update({'user_id': call.message.chat.id})
    await bot.answer_callback_query(call.id, "Пропуск названия", show_alert=False)
    await call.message.delete()
    try:
        await add_wallet(data)
        await bot.send_message(call.message.chat.id, f'Кошелек {data.get("address")} успешно добавлен.')
        await state.reset_state()
    except HTTPStatusError as e:
        if e.response.status_code == 409:
            await bot.send_message(call.message.chat.id, 'Адрес в указаной сети уже существует. '
                                                         'Введите другой адрес кошелька.')
            await states.Wallet.address.set()
    except ServerError:
        await bot.send_message(
            call.message.chat.id,
            f'Произошла ошибка при добавлении кошелька: {data.get("address")} Попробуйте снова.'
        )
        await state.reset_state()


@dp.callback_query_handler(state=states.Wallet.address)
async def cancel_handler(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id, "Отмена", show_alert=False)
    await call.message.edit_text(
        f'⬇️Выберите нужную категорию на клавиатуре.⬇️',
    )
    await state.reset_state()


@dp.callback_query_handler(state=states.Settings.wallets)
async def wallet_list_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    wallets = data.get('wallets')
    wallets_id = [obj['id'] for obj in wallets]
    if call.data in wallets_id:
        await call.message.edit_text(f'Выбран кошелек: {wallets[call.data]["address"]}',
                                     reply_markup=inline_kb.back_kb)
    if call.data == 'back':
        await send_wallets(call, state, data.get('wallet_index'))


@dp.callback_query_handler(state=states.Settings.change_name)
async def change_name_call_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == 'back':
        await send_wallets(call, state, data.get('wallet_index'))


@dp.message_handler(state=states.Settings.change_name)
async def change_name_message_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await update_wallet(data['wallets'][data['wallet_index']]['id'], {'description': message.text})
    await message.answer('Описание изменено.')


@dp.callback_query_handler(state=states.Settings.view_list)
async def view_list_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == 'back':
        await send_wallets(call, state, data.get('wallet_index'))
