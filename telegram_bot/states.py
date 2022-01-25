from aiogram.dispatcher.filters.state import StatesGroup, State


class Wallet(StatesGroup):
    chain = State()
    address = State()
    name = State()


class Referral(StatesGroup):
    info = State()


class Settings(StatesGroup):
    choice = State()
    wallets = State()
    transactions = State()
    filters = State()
    subscription_info = State()
    change_name = State()
    view_list = State()
    stats = State()


class Filter(StatesGroup):
    limit_currency = State()
    limit_tokens = State()
    limit_native = State()


class Stats(StatesGroup):
    address = State()
    name = State()
    start_timestamp = State()
    end_timestamp = State()


class Feedback(StatesGroup):
    message = State()
