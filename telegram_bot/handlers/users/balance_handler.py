import json
import websockets
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from aiogram import types
import logging
from django.conf import settings

from telegram_bot.loader import dp
from telegram_bot.utils.render import render_link


def render_text(obj: dict, total_balances: dict, amounts: dict) -> str:
    total = round(obj["balance"] * obj["price"], 2)
    text = f'<b>Баланс кошелька {obj["chain"].upper()}:</b>\n' \
           f'{render_link(obj.get("description"), obj["wallet"], obj["chain"], "address")}\n' \
           f'Всего токенов: {len(obj["tokens"])}\n\n' \
           f'<b>{obj["chain"].upper()}</b> ({obj["name"]}): {round(obj["balance"], 6)} ' \
           f'<code>({total} USD)</code> \n'

    total_balances.update({f'{obj["chain"]}': total_balances.get(obj["chain"], 0) + total})
    amounts.update({f'{obj["chain"]}': amounts.get(obj["chain"], 0) + obj["balance"]})
    for token in obj["tokens"]:
        #todo fix balance
        text += f'\n<b>{token["symbol"]}</b> ' \
                f'({render_link(token.get("name"), token["token_address"], obj["chain"], "token")}): ' \
                f'{round(token["balance"], 6)} '
        if token.get('price'):
            token_total = round(token["price"] * token["balance"], 2)
            total_balances.update({'tokens': total_balances.get('tokens', 0) + token_total})
            text += f'<code>[{token_total} USD]</code>'
    return text


@dp.message_handler(text='Баланс', state='*')
async def check_balance(message: types.Message):
    balances = []
    total_balances = {'tokens': 0}
    amounts = {}
    async with websockets.connect(settings.BASE_SERVER_WS + f'/balances/{message.from_user.id}') as client:
        try:
            while True:
                data = await client.recv()
                obj = json.loads(data)
                await message.answer(render_text(obj, total_balances, amounts), disable_web_page_preview=True)
                balances.append(obj)
        except ConnectionClosedError:
            logging.error('Connection Error')
            await message.answer('Произошла ошибка соединения с сервером. Попробуйте снова.')
        except ConnectionClosedOK:
            if not balances:
                await message.answer('Вы еще не добавили ни одного кошелька.\n'
                                     '⬇️Нажмите кнопку добавить кошелек на клавиатуре⬇️')
            else:
                text = '<b>Общий баланс на всех кошельках:</b>\n\n'
                for key, value in amounts.items():
                    text += f'<b>{key.upper()}:</b> {round(value, 7)} <code>[{total_balances[key]} USD]</code>\n'
                text += f'<b>\nСумма токенов:</b> <code>[{round(total_balances["tokens"], 2)} USD]</code>\n' \
                        f'<b>Общая сумма:</b> <code>[{round(sum([value for value in total_balances.values()]), 2)} ' \
                        f'USD]</code>'
                await message.answer(text, disable_web_page_preview=True)
