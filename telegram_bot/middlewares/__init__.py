from aiogram import Dispatcher
from django.conf import settings

from .throttling import ThrottlingMiddleware
from .language import ACLMiddleware
from .users import UserMiddleware


def setup(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(UserMiddleware())


def setup_i18n(dp: Dispatcher):
    i18n = ACLMiddleware(settings.I18N_DOMAIN, settings.LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n
