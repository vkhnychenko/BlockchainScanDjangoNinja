from typing import List
from ninja.errors import HttpError
from collections import defaultdict
from datetime import datetime

from .coingecko import CoinGeckoAPI
from .etherscan import get_tx_from_scan
from ..models import Wallet, StatsWallet
from ..schemas import StatsFilterCreate, StatsFilterOut

cg = CoinGeckoAPI()


def add_stats_wallet(data: StatsFilterCreate) -> StatsFilterOut:
    dict_data = data.dict()
    try:
        wallet = Wallet.objects.get(pk=dict_data['wallet_id'])
    except Wallet.DoesNotExist:
        raise HttpError(404, "Not found")
    try:
        StatsWallet.objects.get(address=dict_data['address'], wallet=wallet)
        raise HttpError(409, 'The filter with the selected wallet has already been added')
    except StatsWallet.DoesNotExist:
        del dict_data['wallet_id']
        return StatsWallet.objects.create(wallet=wallet, **dict_data)


def get_stats_wallet(pk: int) -> StatsFilterOut:
    return StatsWallet.objects.select_related('wallet').get(pk=pk)


def get_stats_wallets(wallet_id: int) -> List[StatsFilterOut]:
    return StatsWallet.objects.select_related('wallet').filter(wallet__id=wallet_id)


def get_normal_tx(wallet_address: str, filter_address: str, chain: str):
    tx = get_tx_from_scan(wallet_address, chain, 'normal')
    output_tx = {}
    input_tx = {}
    native_price = {}
    for obj in tx:

        if obj['to'] == filter_address.lower():
            date = datetime.fromtimestamp(int(obj['timeStamp'])).strftime('%d-%m-%Y')

            if not native_price.get(date):
                native_price[date] = cg.get_price_native_coin_history(chain, date)
            output_tx.update({
                'value': output_tx.get('value', 0) + int(obj['value']) / 10 ** 18,
                'count': output_tx.get('count', 0) + 1,
                'tx_cost': output_tx.get('tx_cost', 0) + int(obj['gasPrice']) * int(
                    obj['gasUsed']) / 10 ** 18 * native_price[date],
                'tx': output_tx.get('tx', []) + [obj['hash']]
            })
        if obj['from'] == filter_address.lower():
            input_tx.update({
                'value': input_tx.get('value', 0) + int(obj['value']) / 10 ** 18,
                'count': input_tx.get('count', 0) + 1,
            })
    return input_tx, output_tx


def get_internal_tx(wallet_address: str, filter_address: str, chain: str):
    tx = get_tx_from_scan(wallet_address, chain, 'internal')
    print(tx)


def get_token_tx(wallet_address: str, filter_address: str, chain: str):
    tx = get_tx_from_scan(wallet_address, chain, 'token')
    native_price = {}
    # tokens_price = defaultdict(dict)
    output_tx = defaultdict(dict)
    input_tx = defaultdict(dict)
    for obj in tx:
        print(obj)
        address = obj['contractAddress']
        date = datetime.fromtimestamp(int(obj['timeStamp'])).strftime('%d-%m-%Y')
        if obj['to'] == filter_address.lower():
            if not native_price.get(date):
                native_price[date] = cg.get_price_native_coin_history(chain, date)
            output_tx[address].update({
                'name': obj['tokenName'],
                'symbol': obj['tokenSymbol'],
                'decimals': obj['tokenDecimal'],
                'value': output_tx[address].get('value', 0) + int(obj['value']) / 10 ** int(obj['tokenDecimal']),
                'count': output_tx[address].get('count', 0) + 1,
                'tx_cost': output_tx[address].get('tx_cost', 0) + int(obj['gasPrice']) * int(
                    obj['gasUsed']) / 10 ** 18 * native_price[date],
                'tx': output_tx[address].get('tx', []) + [obj['hash']]
            })
        if obj['from'] == filter_address.lower():
            input_tx[address].update({
                'name': obj['tokenName'],
                'symbol': obj['tokenSymbol'],
                'decimals': obj['tokenDecimal'],
                'value': input_tx[address].get('value', 0) + int(obj['value']) / 10 ** int(obj['tokenDecimal']),
                'count': input_tx[address].get('count', 0) + 1,
                'tx': input_tx[address].get('tx', []) + [obj['hash']]
            })

    return input_tx, output_tx


def get_transaction(filter_id: int):
    filter_obj = get_stats_wallet(filter_id)
    token_input, token_output = get_token_tx(filter_obj.wallet.address, filter_obj.address, filter_obj.wallet.chain)
    normal_input, normal_output = get_normal_tx(filter_obj.wallet.address, filter_obj.address, filter_obj.wallet.chain)

    return {'normal_input': normal_input, 'normal_output': normal_output,
            'token_input': token_input, 'token_output': token_output}
