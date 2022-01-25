import httpx
from httpx._exceptions import ConnectError, TimeoutException, RequestError, TooManyRedirects
import logging
from django.conf import settings
from aiogram import types

from .exceptions import ServerError


async def server_request(url: str, method: str, data: dict = None, payload: dict = None):
    if not payload:
        payload = {'api_key': settings.SERVER_API_KEY}
    else:
        payload['api_key'] = settings.SERVER_API_KEY
    async with httpx.AsyncClient() as client:
        try:
            if method == 'get':
                resp = await client.get(settings.BASE_SERVER_URL + url, params=payload, timeout=30)
                resp.raise_for_status()
                return resp.json()
            elif method == 'post':
                resp = await client.post(settings.BASE_SERVER_URL + url, params=payload, json=data, timeout=30)
                resp.raise_for_status()
                return resp.json()
            elif method == 'delete':
                resp = await client.delete(settings.BASE_SERVER_URL + url, params=payload, timeout=30)
                resp.raise_for_status()
                return resp.json()
        except (ConnectError, TimeoutException, TooManyRedirects, RequestError) as e:
            logging.error(e)
            raise ServerError(e)


async def get_or_create_user(user: types.User):
    user_dict = user.to_python()
    del user_dict['is_bot']
    return await server_request('/users/bot', method='post', data=user_dict)


async def update_user(user_id: int, data: dict):
    return await server_request(f'/users/bot/{user_id}', method='post', data=data)


async def add_wallet(data: dict):
    return await server_request('/wallet/', method='post', data=data)


async def update_wallet(wallet_id: int, data: dict):
    return await server_request(f'/wallet/{wallet_id}', method='post', data=data)


async def delete_wallet(wallet_id: int):
    return await server_request(f'/wallet/{wallet_id}', method='delete')


async def get_wallets(user_id: int):
    payload = {'bot_user_id': user_id}
    return await server_request('/wallet/', method='get', payload=payload)


async def get_balances(user_id: int):
    payload = {'bot_user_id': user_id}
    return await server_request('/wallet/balances', method='get', payload=payload)


async def get_referrals(user_id: int):
    payload = {'bot_user_id': user_id}
    return await server_request('/users/referrals', method='get', payload=payload)


async def get_transactions(user_id: int):
    payload = {'bot_user_id': user_id}
    return await server_request('/wallet/transactions/', method='get', payload=payload)


async def add_stats_wallet(data: dict):
    return await server_request('/wallet/stats/', method='post', data=data)


async def delete_stats_wallet(wallet_id: int):
    return await server_request(f'/wallet/stats/{wallet_id}', method='delete')


async def update_stats_wallet(wallet_id: int, data: dict):
    return await server_request(f'/wallet/stats/{wallet_id}', method='post', data=data)


async def get_stats_wallets(wallet_id: int):
    payload = {'wallet_id': wallet_id}
    return await server_request('/wallet/stats/', method='get', payload=payload)


async def get_stats_transactions(stats_wallet_id: int):
    return await server_request(f'/wallet/stats/tx/{stats_wallet_id}', method='get')


async def get_lang(user_id: int) -> str:
    pass

