import httpx
from httpx._exceptions import ConnectError, TimeoutException, RequestError, TooManyRedirects, HTTPStatusError
import logging
from typing import Union, List
from django.conf import settings

from wallets.utils import convert_balance, get_or_create_token_contract, get_tokens_price


def moralis_auth() -> str:
    payload = {'key': settings.MORALIS_API_KEY}
    with httpx.Client() as client:
        try:
            resp = client.post(settings.MORALIS_BASE_URL + '/account/generateToken', params=payload)
            resp.raise_for_status()
            json_data = resp.json()
            return json_data
        except (RequestError, ConnectError, TimeoutException, TooManyRedirects, HTTPStatusError) as e:
            logging.error(e)


def get_moralis_info(url: str, method: str, payload: dict = None) -> Union[dict, List[dict]]:
    token = moralis_auth()
    headers = {
        'Authorization': f'Bearer {token}'
    }
    with httpx.Client() as client:
        try:
            if method == 'get':
                resp = client.get(settings.MORALIS_BASE_URL + url, headers=headers, params=payload)
            elif method == 'post':
                resp = client.post(settings.MORALIS_BASE_URL + url, headers=headers, params=payload)
            resp.raise_for_status()
            # print(resp.json())
            return resp.json()
        except (RequestError, ConnectError, TimeoutException, TooManyRedirects, HTTPStatusError) as e:
            logging.error(e)


def get_balance_from_moralis(address: str, chain: str) -> float:
    payload = {'chain': chain,
               'chain_name': 'mainnet',
               'address': address}
    resp = get_moralis_info('/account/balance', method='get', payload=payload)
    return convert_balance(resp['balance'], settings.CHAIN_DECIMALS[chain])


def get_erc20_balances_from_moralis(address: str, chain: str) -> List[dict]:
    payload = {'chain': chain,
               'chain_name': 'mainnet',
               'address': address}
    tokens = get_moralis_info('/account/erc20/balances', method='get', payload=payload)
    if tokens:
        for token in tokens:
            get_or_create_token_contract(token['token_address'], chain, name=token['name'],
                                         symbol=token['symbol'], decimals=token['decimals'])
            token['balance'] = convert_balance(token['balance'], token['decimals'])
        get_tokens_price(tokens, chain, 'usd')
    return tokens


def get_events_from_moralis(address: str, chain: str) -> List[dict]:
    payload = {'chain': chain,
               'chain_name': 'mainnet',
               'address': address,
               'topic': 'Transfer()'}
    data = get_moralis_info('/historical/events', method='post', payload=payload)
    return data


def get_token_tx_from_moralis(address: str, chain: str, block_number: int = None) -> List[dict]:
    payload = {'chain': chain,
               'chain_name': 'mainnet',
               'address': address,
               'from_block': block_number
               }
    data = get_moralis_info('/historical/token/erc20/transactions', method='get', payload=payload)
    return data


def get_native_tx_from_moralis(address: str, chain: str, block_number: int = None) -> List[dict]:
    payload = {'chain': chain,
               'chain_name': 'mainnet',
               'address': address,
               'from_block': block_number
               }
    data = get_moralis_info('/historical/native/transactions', method='get', payload=payload)
    return data
