from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


balance = KeyboardButton('Баланс')
wallets = KeyboardButton('Кошельки')
settings = KeyboardButton('Настройки')
partner = KeyboardButton('Партнерская программа')
feedback = KeyboardButton('Обратная связь')
donate = KeyboardButton('Поддержать проект')
language = KeyboardButton('Язык')


start_kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
start_kb.add(balance)
start_kb.row(wallets, settings)
start_kb.row(partner, feedback)
start_kb.row(language, donate)
