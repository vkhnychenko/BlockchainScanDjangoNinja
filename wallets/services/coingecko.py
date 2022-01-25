import os
import logging
import random

import httpx
from tenacity import retry, stop_after_attempt


class CoinGeckoAPI:
    __API_URL_BASE = 'https://api.coingecko.com/api/v3/'

    def __init__(self, api_base_url=__API_URL_BASE):
        self.api_base_url = api_base_url
        self.request_timeout = 5
        self.proxy_list = self.read_proxy(os.path.abspath("proxies.txt"))
        self.platform_idx = {
            'eth': 'ethereum',
            'bsc': 'binance-smart-chain',
            'polygon': 'polygon-pos'
        }
        self.native_idx = {
            'bsc': 'binancecoin',
            'eth': '',
            'polygon': ''
        }

    @staticmethod
    def read_proxy(file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read().split('\n')
        except FileNotFoundError:
            return []

    @staticmethod
    def __api_url_params(api_url, params, api_url_has_params=False):
        if params:
            api_url += '&' if api_url_has_params else '?'
            for key, value in params.items():
                if type(value) == bool:
                    value = str(value).lower()

                api_url += f"{key}={value}&"
            api_url = api_url[:-1]
        return api_url

    @retry(stop=stop_after_attempt(5))
    def __request(self, url):
        proxies = {}
        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            proxies = {
                "http://": f"http://{proxy}",
                "https://": f"http://{proxy}"
            }
        try:
            with httpx.Client(proxies=proxies) as client:
                try:
                    resp = client.get(url, timeout=self.request_timeout)
                except httpx._exceptions.RequestError as e:
                    logging.error(e)
                    raise
                try:
                    resp.raise_for_status()
                    return resp.json()
                except Exception as e:
                    logging.error(e)
                    raise
        except httpx._exceptions.ProxyError:
            raise

    def get_coins_list(self, **kwargs):
        """List all supported coins id, name and symbol (no pagination required)"""

        api_url = f'{self.api_base_url}coins/list'
        api_url = self.__api_url_params(api_url, kwargs)

        return self.__request(api_url)

    def get_token_price(self, contract_addresses: str, chain: str,  vs_currencies: str, **kwargs) -> dict:
        """Get the current price of any tokens on this coin (ETH only at this stage as per api docs)
         in any other supported currencies that you need"""

        kwargs['contract_addresses'] = contract_addresses.replace(' ', '')
        kwargs['vs_currencies'] = vs_currencies.replace(' ', '')

        api_url = f'{self.api_base_url}simple/token_price/{self.platform_idx[chain]}'
        api_url = self.__api_url_params(api_url, kwargs)
        return self.__request(api_url)

    def get_coin_history_by_id(self, idx, date, **kwargs):
        """Get historical data (name, price, market, stats) at a given date for a coin"""

        kwargs['date'] = date

        api_url = f'{self.api_base_url}coins/{idx}/history'
        api_url = self.__api_url_params(api_url, kwargs)

        return self.__request(api_url)

    def get_price_native_coin_history(self, chain: str, date: str, currency: str = 'usd', **kwargs):
        kwargs['date'] = date

        api_url = f'{self.api_base_url}coins/{self.native_idx[chain]}/history'
        api_url = self.__api_url_params(api_url, kwargs)
        data = self.__request(api_url)

        return data['market_data']['current_price'][currency]

    def get_coin_market_chart_range_from_contract_address_by_id(self, chain, contract_address, vs_currency,
                                                                      from_timestamp = 1617846423, to_timestamp = 1627846423, **kwargs):
        """Get historical market data include price, market cap, and 24h volume within a range of timestamp
         (granularity auto) from a contract address"""

        api_url = f'{self.api_base_url}coins/{self.platform_idx[chain]}/contract/{contract_address}/' \
                  f'market_chart/range?vs_currency={vs_currency}&from={from_timestamp}&to={to_timestamp}'
        api_url = self.__api_url_params(api_url, kwargs)

        return self.__request(api_url)

    def get_asset_platforms(self, **kwargs):
        """List all asset platforms (Blockchain networks)"""

        api_url = f'{self.api_base_url}asset_platforms'
        api_url = self.__api_url_params(api_url, kwargs)

        return self.__request(api_url)

# async def get_coins_list_from_cg() -> dict:
#     try:
#         return cg.get_coins_list()
#     except Exception as e:
#         logging.error(e)
#         return {}
#
#
# async def get_token_price_from_cg(address: str, chain: str, currencies: List[str]) -> dict:
#
#     try:
#         return cg.get_token_price(cg_tokens_platform[chain], address, vs_currencies=currencies)
#     except Exception as e:
#         logging.error(e)
#         return {}


# async def get_native_price_history_from_cg(chain: str, date: str = '29-07-2021', currency: str = 'usd') -> int:
#     tickers = {'bsc': 'binancecoin', 'eth': '', 'polygon': ''}
#     try:
#         return cg.get_coin_history_by_id(tickers[chain], date)['market_data']['current_price'][currency]
#     except Exception as e:
#         logging.error(e)
#         return 1
