from aiogram.utils.markdown import hlink
from django.conf import settings


def render_link(name: str, address: str, chain: str, tx_type: str):
    name = name if name else address
    groups = {
        'address': hlink(name, settings.URLS_SCAN[chain] + "address/" + address),
        'tx': hlink(name, settings.URLS_SCAN[chain] + "tx/" + address),
        'token': hlink(name, settings.URLS_SCAN[chain] + "token/" + address)
    }
    return groups[tx_type]
