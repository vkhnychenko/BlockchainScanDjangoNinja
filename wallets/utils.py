from collections import defaultdict
from typing import List, Union

from .services.coingecko import CoinGeckoAPI
from .models import TokenContract, Transaction

cg = CoinGeckoAPI()


def get_or_create_token_contract(address, chain, name=None, symbol=None, decimals=None):
    try:
        obj = TokenContract.objects.get(token_address=address, chain=chain)
        obj.name = name if name else obj.name
        obj.symbol = symbol if symbol else obj.symbol
        obj.decimals = decimals if decimals else obj.decimals
        obj.save()
        return obj
    except TokenContract.DoesNotExist:
        return TokenContract.objects.create(token_address=address, chain=chain, name=name,
                                            symbol=symbol, decimals=decimals)


def get_tokens_price_for_transaction(tx_list: List[Transaction], currency: str):
    addresses = defaultdict(str)
    for tx in tx_list:
        if tx.token_contract:
            addresses[tx.wallet.chain] += f',{tx.token_contract.token_address}'
    prices = {}
    for chain in addresses.keys():
        prices.update(cg.get_token_price(addresses[chain], chain, currency))
    for tx in tx_list:
        if tx.token_contract:
            token_price = prices.get(tx.token_contract.token_address.lower())
            if token_price:
                tx.token_price = token_price[currency]


def get_tokens_price(tokens: dict, chain, currency: str):
    addresses = [token["token_address"] for token in tokens]
    addresses = ','.join(addresses)
    prices = cg.get_token_price(addresses, chain, currency)
    for token in tokens:
        token_price = prices.get(token['token_address'].lower())
        if token_price:
            token['price'] = token_price[currency]


def convert_balance(value: Union[str, int], decimal: Union[str, int]) -> float:
    return int(value) / 10 ** int(decimal)
