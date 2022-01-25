from typing import List, Union
from web3 import Web3
from django.utils.timezone import now

from .etherscan import get_price_native_from_scan, get_last_block_number_from_scan
from .moralis import get_token_tx_from_moralis, get_native_tx_from_moralis
from ..models import Transaction, Wallet
from ..utils import get_tokens_price_for_transaction, get_or_create_token_contract

w3 = Web3(Web3.WebsocketProvider())


def get_transactions_for_user(user_id: int, chain: str) -> List[Transaction]:
    if chain:
        return Transaction.objects.filter(wallet__user__id=user_id, wallet__chain=chain)
    return Transaction.objects.filter(wallet__user__id=user_id)


def parse_tx(tx_list: List[dict], tx_type: str, wallet: Wallet, native_prices: dict, ) -> List[Transaction]:
    new_tx = []
    for tx in tx_list:
        if int(tx['block_number']) > wallet.last_tx_block_number:
            tx_obj = Transaction(wallet=wallet, to_address=tx['to_address'], from_address=tx['from_address'],
                                 value=tx['value'], native_price=native_prices[wallet.chain])
            if tx_type == 'token':
                tx_obj.hash = tx['transaction_hash']
                tx_obj.type = 'token'
                tx_obj.token_contract = get_or_create_token_contract(tx['address'], wallet.chain)
                tx_obj.tx_fee = tx.get('tx_fee')

            elif tx_type == 'native':
                tx_obj.hash = tx['hash']
                tx_obj.type = 'native'
                tx_obj.tx_fee = int(tx['gas_price']) * int(tx['receipt_gas_used'])

            new_tx.append(tx_obj)
    return new_tx


def check_identical_tx(tokens_tx: List[dict], native_tx: List[dict]):
    for n_tx in native_tx:
        for t_tx in tokens_tx:
            if n_tx['hash'] in t_tx.values():
                t_tx.update({'tx_fee': int(n_tx['gas_price']) * int(n_tx['receipt_gas_used'])})
                try:
                    native_tx.remove(n_tx)
                except ValueError:
                    pass


def get_last_block_number(token_tx: list, native_tx: list) -> Union[int, None]:
    token_block_number = int(token_tx[0].get('block_number')) if len(token_tx) > 0 else 0
    native_block_number = int(native_tx[0].get('block_number')) if len(native_tx) > 0 else 0
    if token_block_number == 0 and native_block_number == 0:
        return None
    elif token_block_number > native_block_number:
        return token_block_number
    else:
        return native_block_number


def get_new_transactions() -> List[Transaction]:
    wallets = Wallet.objects.all()
    new_trans = []
    native_prices = {'eth': get_price_native_from_scan('eth'),
                     'bsc': get_price_native_from_scan('bsc'),
                     'polygon': get_price_native_from_scan('polygon')}

    for wallet in wallets:
        if not wallet.last_tx_block_number:
            wallet.last_tx_block_number = get_last_block_number_from_scan(wallet.last_tx_timestamp, wallet.chain)
        tokens_tx = get_token_tx_from_moralis(wallet.address, wallet.chain,
                                              block_number=wallet.last_tx_block_number)
        native_tx = get_native_tx_from_moralis(wallet.address, wallet.chain,
                                               block_number=wallet.last_tx_block_number)
        check_identical_tx(tokens_tx, native_tx)
        new_trans += parse_tx(tokens_tx, 'token', wallet, native_prices)
        new_trans += parse_tx(native_tx, 'native', wallet, native_prices)

        last_tx_block_number = get_last_block_number(tokens_tx, native_tx)
        if last_tx_block_number:
            wallet.last_tx_block_number = last_tx_block_number
        wallet.last_tx_timestamp = int(now().timestamp())
        wallet.save()

    Transaction.objects.bulk_create(new_trans)
    get_tokens_price_for_transaction(new_trans, 'usd')
    return new_trans
