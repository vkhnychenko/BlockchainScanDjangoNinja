import asyncio
import logging
from time import sleep
from decimal import Decimal

from config.celery import app
from telegram_bot.loader import bot
from wallets.models import WalletChain, Transaction
from wallets.services.one_inch import get_one_inch_tokens
from wallets.services.transactions import get_new_transactions
from aiogram.utils.exceptions import ChatNotFound, RetryAfter

from telegram_bot.utils.render import render_link
from telegram_bot.loader import w3
from wallets.utils import get_or_create_token_contract


def render_tx_native_text(tx: Transaction, chain, names):
    value = w3.fromWei(int(tx.value), 'ether')
    text = f'{value} <b>{chain.upper()}</b>({names[chain]}): '
    text += f'<code>{round(value * Decimal(tx.native_price)), 2} USD</code>' if value else ''
    return text


def render_tx_token_text(tx: Transaction, chain, names) -> str:
    token_name = tx.token_contract.symbol if tx.token_contract.symbol else ''
    value = Decimal(int(tx.value) / 10 ** tx.token_contract.decimals) if tx.token_contract.decimals else w3.fromWei(int(tx.value), 'ether')
    link = render_link(tx.token_contract.name, tx.token_contract.token_address, chain, "token")
    text = f'{round(value, 6)} <b>{token_name}</b>({link}): '
    text += f'<code>{round(Decimal(tx.token_price) * value, 2)} USD</code>' if tx.token_price else ''
    return text


def render_new_tx_text(tx: Transaction) -> str:
    tx_fee = w3.fromWei(int(tx.tx_fee), 'ether') if tx.tx_fee else ''
    my_address = tx.wallet.address.lower()
    chain = tx.wallet.chain
    names = {'eth': 'Ethereum', 'bsc': 'Binance', 'polygon': 'Polygon(Matic)'}
    text_to_type = {'token': render_tx_token_text, 'native': render_tx_native_text}
    wallet_link = render_link(tx.wallet.description, tx.wallet.address, chain, 'address')
    text = f'{wallet_link}\n'
    if tx.to_address.lower() == my_address:
        text += f'➕{text_to_type[tx.type](tx, chain, names)}\n' \
                f'FROM {render_link(tx.from_address, tx.from_address, chain, "address")}\n'
    elif tx.from_address.lower() == my_address:
        text += f'➖{text_to_type[tx.type](tx, chain, names)}\n' \
                f'TO {render_link(tx.to_address, tx.to_address, chain, "address")}\n'
        text += f'<b>TX FEE: {tx_fee}</b> <code>({round(tx_fee * Decimal(tx.native_price), 2)}) USD</code>\n' if tx_fee else ''
    text += f'<code>(</code>{render_link("View on Explorer", tx.hash, chain, "tx")}<code>)</code>'
    return text


async def send_message(chat_id, msg):
    await bot.send_message(chat_id, msg, disable_web_page_preview=True)


@app.task
def new_transactions_notification():
    loop = asyncio.get_event_loop()
    tx_list = get_new_transactions()
    logging.info(f'new transactions {tx_list}')
    for tx in tx_list:
        for i in range(5):
            try:
                loop.run_until_complete(send_message(tx.wallet.user.id, render_new_tx_text(tx)))
                break
            except ChatNotFound:
                pass
            except RetryAfter:
                logging.error('RetryAfter')
                sleep(5)


@app.task
def get_tokens_info():
    for chain in WalletChain:
        tokens_info = get_one_inch_tokens(chain[0])
        for key, value in tokens_info['tokens'].items():
            get_or_create_token_contract(key, chain[0], name=value.get('name'), symbol=value.get('symbol'),
                                         decimals=value.get('decimals'))
