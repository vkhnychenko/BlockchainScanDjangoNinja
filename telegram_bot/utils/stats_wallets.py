from aiogram import types
from datetime import datetime

from telegram_bot.keyboards import inline_keyboards as inline_kb
from telegram_bot.utils.render import render_link


def render_stats_text(obj: dict):
    wallet = obj["wallet"]
    text = f'Основной кошелек: {render_link(wallet.get("description"), wallet["address"], wallet["chain"], "address")}\n'
    text += f'Кошелек для анализа: {render_link(obj.get("description"), obj["address"], wallet["chain"], "address")}\n'
    text += f'Дата начала транзакций: {datetime.fromtimestamp(obj["start_timestamp"]).strftime("%d-%m-%Y")}\n' if obj.get("start_timestamp") else ''
    text += f'Дата окончания транцакций: {datetime.fromtimestamp(obj["end_timestamp"]).strftime("%d-%m-%Y")}\n' if obj.get("end_timestamp") else ''
    return text


async def render_stats_wallets(call: types.CallbackQuery, wallets: list, index: int):
    quantity = len(wallets)
    kb = inline_kb.stats_kb(quantity, index)
    await call.message.edit_text(render_stats_text(wallets[index]), reply_markup=kb,
                                 disable_web_page_preview=True)


def render_normal_tx_text(tx: dict, address: str, tx_type: str, currency: str):
    text = f'Входящие транзакции с кошелька: ' if tx_type == 'input' else 'Исходящие транзакции в кошелек: '
    text += f'<b>{address}</b>\n\n'
    text += f'Общая сумма: <b>{tx["value"]} {currency}</b>\n'
    text += f'Количество транзакций: <b>{tx["count"]}</b>\n'
    text += f'Комиссия за транзакции: <b>{tx["tx_cost"]} USDT</b>' if tx_type == 'output' else ''
    return text


def render_token_tx_text(tx: dict, address: str, tx_type: str):
    text = f'Входящие транзакции токенов с кошелька: ' if tx_type == 'input' else 'Исходящие транзакции токенов в кошелек: '
    text += f'<b>{address}</b>\n\n'
    for key in tx.keys():
        text += f'Токен: <b>{tx[key]["symbol"]}</b>\n'
        text += f'Общая сумма: <b>{tx[key]["value"]} {tx[key]["symbol"]}</b>\n'
        text += f'Количество транзакций: <b>{tx[key]["count"]}</b>\n'
        text += f'Комиссия за транзакции: <b>{tx[key]["tx_cost"]} USDT</b>' if tx_type == 'output' else ''
    return text
