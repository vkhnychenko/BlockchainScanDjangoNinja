from aiogram import types
from aiogram.dispatcher import FSMContext

from telegram_bot.keyboards import inline_keyboards as inline_kb
from telegram_bot import states
from telegram_bot.utils import server_api
from telegram_bot.utils.render import render_link


def render_wallets_text(wallet: dict) -> str:
    text = f'Имя кошелька: {wallet["description"]}\n' if wallet["description"] else ''
    text += f'Сеть кошелька: {wallet["chain"].upper()}\n' \
            f'Адрес кошелька: {render_link(None, wallet["address"], "bsc", "address")}\n'
    return text


async def render_wallets(call: types.CallbackQuery, wallets: list, index: int):
    quantity = len(wallets)
    kb = inline_kb.wallets_kb(quantity, index, show_balance=wallets[index]['show_balance'])
    await call.message.edit_text(render_wallets_text(wallets[index]), reply_markup=kb,
                                 disable_web_page_preview=True)


async def send_wallets(call: types.CallbackQuery, state: FSMContext, index: int):
    index = index if index else 0
    data = await state.get_data()
    wallets = data['wallets'] if data.get('wallets') else await server_api.get_wallets(call.message.chat.id)
    if not wallets:
        await call.answer("У вас еще нет добавленных кошельков", show_alert=False)
        await call.message.edit_text('У вас еще нет добавленных кошельков', reply_markup=inline_kb.back_kb)
    else:
        await call.answer(f"{index + 1} кошелек из {len(wallets)}.", show_alert=False)
        await render_wallets(call, wallets, index)
    await state.update_data(wallets=wallets, wallet_index=index)
    await states.Settings.wallets.set()
