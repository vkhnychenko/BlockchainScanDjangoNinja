from typing import List

from .etherscan import get_price_native_from_scan
from ..services.moralis import get_balance_from_moralis, get_erc20_balances_from_moralis
from users.models import UserBot


def get_balance(address: str, chain: str, description: str = None) -> dict:
    names = {'eth': 'Ethereum', 'bsc': 'Binance', 'polygon': 'Polygon(Matic)'}
    balance = {
        'name': names[chain],
        'wallet': address,
        'chain': chain,
        'description': description,
        'balance': get_balance_from_moralis(address, chain),
        'price': get_price_native_from_scan(chain),
        'tokens': get_erc20_balances_from_moralis(address, chain)
    }
    return balance


def get_balances(user_id: int, chain: str = None) -> List[dict]:
    user = UserBot.objects.get(id=user_id)
    if chain:
        wallets = user.wallets.filter(chain=chain)
    else:
        wallets = user.wallets.all()
    for wallet in wallets:
        yield get_balance(wallet.address, wallet.chain, wallet.description)
