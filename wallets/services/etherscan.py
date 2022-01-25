import httpx
from httpx._exceptions import ConnectError, TimeoutException, RequestError, TooManyRedirects, HTTPStatusError
import logging
from typing import Union, List
from django.conf import settings


def get_scan_info(payload: dict, chain: str) -> Union[dict, List[dict], int]:
    urls = {'eth': settings.ETH_API_URL, 'bsc': settings.BSC_API_URL, 'polygon': settings.POLYGON_API_URL}
    api_keys = {'eth': settings.ETH_API_KEY, 'bsc': settings.BSC_API_KEY, 'polygon': settings.POLYGON_API_KEY}
    payload['apikey'] = api_keys[chain]
    with httpx.Client() as client:
        try:
            resp = client.get(urls[chain], params=payload)

            resp.raise_for_status()
            json_data = resp.json()
            try:
                if json_data['status'] != '1':
                    raise RequestError(f"{json_data['message']} - {json_data['result']}")
            except KeyError:
                pass
            return json_data['result']
        except (RequestError, ConnectError, TimeoutException, TooManyRedirects, HTTPStatusError) as e:
            logging.error(e)


def get_price_native_from_scan(chain: str) -> Union[float, None]:
    actions = {'eth': 'ethprice', 'bsc': 'bnbprice', 'polygon': 'maticprice'}
    payload = {'module': 'stats', 'action': actions[chain]}
    data = get_scan_info(payload, chain)
    try:
        if chain == 'polygon':
            return float(data['maticusd'])
        return float(data['ethusd'])
    except (ValueError, TypeError):
        return None


def get_last_block_number_from_scan(timestamp: int, chain: str) -> int:
    payload = {'module': 'block', 'action': 'getblocknobytime', 'timestamp': timestamp, 'closest': 'before'}
    return get_scan_info(payload, chain)


def get_tx_from_scan(address: str, chain: str, tx_type: str,
                                  start_block: int = None, end_block: int = None) -> List[dict]:
    types = {'normal': 'txlist', 'internal': 'txlistinternal', 'token': 'tokentx'}
    payload = {'address': address, 'module': 'account', 'action': types[tx_type], 'sort': 'asc',
               'startblock': start_block, 'endblock': end_block}
    return get_scan_info(payload, chain)


def get_tx_by_hash_from_scan(tx_hash: str, chain: str) -> List[dict]:
    payload = {'txhash': tx_hash, 'module': 'proxy', 'action': 'eth_getTransactionByHash'}
    return get_scan_info(payload, chain)


#https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash=0x1e2910a262b1008d0616a0beb24c1a491d78771baa54a33e66065e03b1f46bc1&apikey=YourApiKeyToken
