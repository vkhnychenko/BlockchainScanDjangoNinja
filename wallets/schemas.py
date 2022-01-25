from datetime import datetime
from ninja import Schema
from ninja.orm import create_schema
from enum import Enum

from .models import Transaction, TokenContract
from users.schemas import UserBotOut, TransactionFilterBase

TransactionOutBase = create_schema(Transaction)
TokenContractBase = create_schema(TokenContract)


class WalletChainEnum(str, Enum):
    eth = 'eth'
    bsc = 'bsc'
    polygon = 'polygon'


class TransactionTypeEnum(str, Enum):
    main = 'main'
    token = 'token'
    nft = 'nft'


#Todo validate address
class WalletBase(Schema):
    address: str
    chain: WalletChainEnum
    description: str = None


class WalletCreate(WalletBase):
    user_id: int


class WalletUpdate(TransactionFilterBase):
    description: str = None
    show_balance: bool = None


class WalletOut(WalletBase):
    id: int
    user: UserBotOut
    native_transfer: bool
    token_transfer: bool
    nft_transfer: bool
    show_balance: bool
    limit_native: int = None
    limit_tokens: int = None
    limit_currency: int = None


class TransactionOut(TransactionOutBase):
    wallet: WalletOut
    token_contract: TokenContractBase = None


class StatsFilterBase(Schema):
    #Todo validate address
    address: str
    description: str = None
    start_timestamp: int = None
    end_timestamp: int = None


class StatsFilterCreate(StatsFilterBase):
    wallet_id: int


class StatsFilterOut(StatsFilterBase):
    id: int
    wallet: WalletBase


class StatsWalletUpdate(Schema):
    description: str = None
    start_timestamp: int = None
    end_timestamp: int = None
