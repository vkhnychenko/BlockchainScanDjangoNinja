from datetime import datetime
from ninja import Schema


class TransactionFilterBase(Schema):
    native_transfer: bool = None
    token_transfer: bool = None
    nft_transfer: bool = None
    limit_native: int = None
    limit_tokens: int = None
    limit_currency: int = None


class UserBotBase(Schema):
    id: int


class UserBotCreate(UserBotBase):
    username: str = None
    first_name: str = None
    last_name: str = None
    language_code: str = None
    referral: int = None


class UserBotOut(UserBotBase):
    username: str = None
    first_name: str = None
    last_name: str = None
    is_active: bool
    language_code: str = None
    referral: int = None
    referral_balance: float = None
    referral_bonus: int
    available_wallets_count: int = None
    wallets_count: int = None
    subscription_is_active: bool
    date_end_subscription: datetime = None
    native_transfer: bool
    token_transfer: bool
    nft_transfer: bool
    limit_native: int = None
    limit_tokens: int = None
    limit_currency: int = None


class UserBotUpdate(TransactionFilterBase):
    pass


class Referral(UserBotBase):
    pass
