from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cancel = InlineKeyboardButton('Отмена', callback_data='cancel')
cancel_kb = InlineKeyboardMarkup(row_width=1)
cancel_kb.add(cancel)

back = InlineKeyboardButton('Назад', callback_data='back')
back_kb = InlineKeyboardMarkup(row_width=1)
back_kb.add(back)

chain_kb = InlineKeyboardMarkup(row_width=3)
chain_kb.insert(InlineKeyboardButton('Ethereum', callback_data='eth'))
chain_kb.insert(InlineKeyboardButton('BSC', callback_data='bsc'))
chain_kb.insert(InlineKeyboardButton('Polygon', callback_data='polygon'))
chain_kb.insert(back)

skip = InlineKeyboardButton('Пропустить', callback_data='skip')
skip_kb = InlineKeyboardMarkup(row_width=1)
skip_kb.add(skip)

referrals_kb = InlineKeyboardMarkup(row_width=3)
referrals_kb.insert(InlineKeyboardButton('Список партнеров', callback_data='referrals'))
referrals_kb.insert(InlineKeyboardButton('Партнерский баланс', callback_data='referral_balance'))

settings_kb = InlineKeyboardMarkup(row_width=1)
settings_kb.insert(InlineKeyboardButton('Последние 100 транзакций', callback_data='last_transactions'))
settings_kb.insert(InlineKeyboardButton('Фильтры', callback_data='filters'))
settings_kb.insert(InlineKeyboardButton('Информация о подписке', callback_data='subscription_info'))

subscription_kb = InlineKeyboardMarkup(row_width=1)
subscription_kb.insert(InlineKeyboardButton('Информация о подписке', callback_data='subscription_info'))

left = InlineKeyboardButton('⬅️', callback_data='left')
right = InlineKeyboardButton('➡️', callback_data='right')


def wallets_kb(quantity: int, i: int = 0, is_empty: bool = False, show_balance: bool = True):
    kb = InlineKeyboardMarkup(row_width=2)
    if is_empty:
        kb.add(InlineKeyboardButton('Добавить новый кошелек', callback_data='add_wallet'))
        return kb
    kb.insert(InlineKeyboardButton('Изменить описание', callback_data='change_name'))
    kb.insert(InlineKeyboardButton('Удалить', callback_data='delete'))
    kb.insert(InlineKeyboardButton('Фильтры', callback_data='filters'))
    kb.insert(InlineKeyboardButton('Аналитика', callback_data='stats'))
    kb.row(left, InlineKeyboardButton(text=f'{i + 1} / {quantity}', callback_data='None'), right)
    kb.add(InlineKeyboardButton('Добавить новый кошелек', callback_data='add_wallet'))
    kb.row(InlineKeyboardButton('Показать списком', callback_data='view_list'))
    kb.add(InlineKeyboardButton(text=f'{"✅" if show_balance else "❌"} Отображение баланса',
                                callback_data='show_balance'))
    return kb


def wallet_list_kb(wallets):
    kb = InlineKeyboardMarkup(row_width=3)
    for wallet in wallets:
        kb.row(
            InlineKeyboardButton(wallet["address"], callback_data=wallet['id'])),
            # InlineKeyboardButton('Фильтры', callback_data='filter'),
            # InlineKeyboardButton('Удалить', callback_data='delete'))
    kb.add(back)
    return kb


def transactions_kb(quantity, i=0):
    kb = InlineKeyboardMarkup(row_width=3)
    kb.row(left, InlineKeyboardButton(text=f'{i + 1} / {quantity}', callback_data='None'), right)
    kb.insert(back)
    return kb


def stats_kb(quantity=None, i=0, is_empty: bool = False):
    kb = InlineKeyboardMarkup(row_width=3)
    if is_empty:
        kb.add(InlineKeyboardButton('Добавить кошелек для аналитики', callback_data='add_stats_wallet'))
        kb.add(back)
        return kb
    kb.row(left, InlineKeyboardButton(text=f'{i + 1} / {quantity}', callback_data='None'), right)
    kb.add(InlineKeyboardButton('Просмотреть историю транзакций', callback_data='stats_balance'))
    kb.add(InlineKeyboardButton('Удалить кошелек для анализа', callback_data='delete_stats_wallet'))
    kb.add(InlineKeyboardButton('Изменить дату начала отслеживания.', callback_data='edit_timestamp_start'))
    kb.add(InlineKeyboardButton('Изменить дату окончания отслеживания.', callback_data='edit_timestamp_end'))
    kb.add(InlineKeyboardButton('Добавить кошелек для анализа', callback_data='add_stats_wallet'))
    kb.add(back)
    return kb


def stats_balance_kb(filters):
    kb = InlineKeyboardMarkup(row_width=3)
    for obj in filters:
        kb.add(InlineKeyboardButton(f'{obj.get("description", obj["address"])}', callback_data=obj["id"]))
    kb.add(back)
    return kb


def filters_kb(data: dict):
    kb = InlineKeyboardMarkup(row_width=3)
    native = InlineKeyboardButton(text=f'{"✅" if data.get("native_transfer") else "❌"} Native transfer',
                                  callback_data='native_transfer')
    token = InlineKeyboardButton(text=f'{"✅" if data.get("token_transfer") else "❌"} Token transfer',
                                 callback_data='token_transfer')
    nft = InlineKeyboardButton(text=f'{"✅" if data.get("nft_transfer") else "❌"} NFT transfer',
                               callback_data='nft_transfer')
    kb.row(native, token)
    kb.add(nft)
    kb.row(InlineKeyboardButton(f'Граница основной валюты', callback_data='limit_native'),
           InlineKeyboardButton(f'Граница токенов', callback_data='limit_tokens'))
    #todo fix choice currency
    kb.add(InlineKeyboardButton(f'Граница USD', callback_data='limit_currency'))
    kb.add(back)
    return kb
