import httpx
from httpx._exceptions import ConnectError, TimeoutException, RequestError, TooManyRedirects, HTTPStatusError
import logging
from typing import Union, List

from django.conf import settings


def get_one_inch_info(url: str, method: str, chain: str, payload: dict = None) -> Union[dict, List[dict]]:
    chain_id = {'eth': 1, 'bsc': 56, 'polygon': 137}
    with httpx.Client() as client:
        try:
            if method == 'get':
                resp = client.get(settings.ONE_INCH_BASE_URL + f'/{chain_id[chain]}' + url, params=payload)
            elif method == 'post':
                resp = client.post(settings.ONE_INCH_BASE_URL + f'/{chain_id[chain]}' + url, params=payload)
            resp.raise_for_status()
            return resp.json()
        except (RequestError, ConnectError, TimeoutException, TooManyRedirects, HTTPStatusError) as e:
            logging.error(e)


def get_one_inch_tokens(chain: str) -> dict:
    return get_one_inch_info('/tokens', 'get', chain)
