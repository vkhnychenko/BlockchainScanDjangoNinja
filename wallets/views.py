from typing import List
from ninja import Router
from ninja.errors import HttpError

from .models import Wallet, StatsWallet
from .schemas import WalletOut, WalletCreate, TransactionOut, StatsFilterCreate, StatsFilterOut, WalletUpdate,\
    StatsWalletUpdate
from .services import wallet, transactions, balance, stats

wallet_router = Router(tags=['wallet'])


@wallet_router.post('/', response=WalletOut)
def create_wallet(request, data: WalletCreate):
    return wallet.add_wallet(data)


@wallet_router.get('/{pk}', response=WalletOut)
def get_wallet(request, pk: int):
    try:
        return Wallet.objects.get(pk=pk)
    except Wallet.DoesNotExist:
        raise HttpError(404, "Not found")


@wallet_router.get('/', response=List[WalletOut])
def get_wallets(request, bot_user_id: int = None):
    return wallet.get_wallets(bot_user_id)


@wallet_router.post('/{pk}')
def update_wallet(request, pk: int, data: WalletUpdate):
    try:
        wal = Wallet.objects.get(pk=pk)
        wal.description = data.description if data.description is not None else wal.description
        wal.show_balance = data.show_balance if data.show_balance is not None else wal.show_balance
        wal.native_transfer = data.native_transfer if data.native_transfer is not None else wal.native_transfer
        wal.token_transfer = data.token_transfer if data.token_transfer is not None else wal.token_transfer
        wal.nft_transfer = data.nft_transfer if data.nft_transfer is not None else wal.nft_transfer
        wal.limit_native = data.limit_native if data.limit_native is not None and data.limit_native >= 0 else wal.limit_native
        wal.limit_tokens = data.limit_tokens if data.limit_tokens is not None and data.limit_tokens >= 0 else wal.limit_tokens
        wal.limit_currency = data.limit_currency if data.limit_currency is not None and data.limit_currency >= 0 else wal.limit_currency
        wal.save()
        return {'status': 'ok'}
    except Wallet.DoesNotExist:
        raise HttpError(404, "Not found")


@wallet_router.delete('/{pk}')
def delete_wallet(request, pk: int):
    try:
        wall = Wallet.objects.get(pk=pk)
        wall.delete()
        return {'status': 'ok'}
    except Wallet.DoesNotExist:
        raise HttpError(404, "Not found")


@wallet_router.get('/balance/{address}')
def get_balance(request, address: str, chain: str):
    return balance.get_balance(address, chain)


@wallet_router.post('/stats/', response=StatsFilterOut)
def add_stats_wallet(request, data: StatsFilterCreate):
    return stats.add_stats_wallet(data)


@wallet_router.delete('/stats/{pk}')
def delete_stats_wallet(request, pk: int):
    try:
        wall = StatsWallet.objects.get(pk=pk)
        wall.delete()
        return {'status': 'ok'}
    except StatsWallet.DoesNotExist:
        raise HttpError(404, "Not found")


@wallet_router.get('/stats/{pk}', response=StatsFilterOut)
def get_stats_wallet(request, pk: int):
    return stats.get_stats_wallet(pk)


@wallet_router.post('/stats/{pk}')
def update_stats_wallet(request, pk: int, data: StatsWalletUpdate):
    try:
        wal = StatsWallet.objects.get(pk=pk)
        wal.description = data.description if data.description is not None else wal.description
        wal.start_timestamp = data.start_timestamp if data.start_timestamp is not None else wal.start_timestamp
        wal.end_timestamp = data.end_timestamp if data.end_timestamp is not None else wal.end_timestamp
        wal.save()
        return {'status': 'ok'}
    except StatsWallet.DoesNotExist:
        raise HttpError(404, "Not found")


@wallet_router.get('/stats/', response=List[StatsFilterOut])
def get_stats_wallets(request, wallet_id: int = None):
    return stats.get_stats_wallets(wallet_id)


@wallet_router.get('/stats/tx/{pk}')
def get_stats_transaction(request, pk: int):
    return stats.get_transaction(pk)


@wallet_router.get('/transactions/', response=List[TransactionOut])
def get_transactions(request, bot_user_id: int = None, chain: str = None):
    return transactions.get_transactions_for_user(bot_user_id, chain)


@wallet_router.get('/new_transactions/', response=List[TransactionOut])
def get_new_transactions(request):
    return transactions.get_new_transactions()

