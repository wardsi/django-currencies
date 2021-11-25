import decimal

import requests

__version__ = '0.1.0'
__author__ = 'Ward and Partners'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021 Ward and Partners'

# https://exchangeratesapi.io/documentation/

class ExchangeRatesApiClientException(requests.exceptions.RequestException):
    """Base client exception wraps all kinds of ``requests`` lib exceptions"""
    pass


class ExchangeRatesApiClient(object):
    """This class is a client implementation for openexchangerate.org service

    """
    BASE_URL = 'http://api.exchangeratesapi.io/v1'
    ENDPOINT_LATEST = BASE_URL + '/latest'
    ENDPOINT_CURRENCIES = BASE_URL + '/symbols'
    ENDPOINT_HISTORICAL = BASE_URL + '/%s'

    def __init__(self, api_key):
        """Convenient constructor"""
        self.client = requests.Session()
        self.client.params.update({'access_key': api_key})

    def latest(self, base='USD'):
        """Fetches latest exchange rate data from service
            https://api.exchangeratesapi.io/v1/latest
                ? access_key = API_KEY
                & base = USD
                & symbols = GBP,JPY,EUR
        :Example Data:
            {
                "success": true,
                "timestamp": 1519296206,
                "base": "USD",
                "date": "2021-03-17",
                "rates": {
                    "GBP": 0.72007,
                    "JPY": 107.346001,
                    "EUR": 0.813399,
                }
            }
        """
        try:
            resp = self.client.get(self.ENDPOINT_LATEST, params={'base': base})
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ExchangeRatesApiClientException(e)
        return resp.json(parse_int=decimal.Decimal,
                         parse_float=decimal.Decimal)

    def currencies(self):
        """Fetches current currency data of the service

        :Example Data:
        {
        "success": true,
        "symbols": {
            "AED": "United Arab Emirates Dirham",
            "AFN": "Afghan Afghani",
            "ALL": "Albanian Lek",
            "AMD": "Armenian Dram",
            [...]
            }
        }
        """
        try:
            resp = self.client.get(self.ENDPOINT_CURRENCIES)
        except requests.exceptions.RequestException as e:
            raise ExchangeRatesApiClientException(e)

        d = resp.json()
        return d['symbols']

    def historical(self, date, base='USD'):
        """Fetches historical exchange rate data from service

        :Example Data:
            {
                disclaimer: "<Disclaimer data>",
                license: "<License data>",
                timestamp: 1358150409,
                base: "USD",
                rates: {
                    AED: 3.666311,
                    AFN: 51.2281,
                    ALL: 104.748751,
                    AMD: 406.919999,
                    ANG: 1.7831,
                    ...
                }
            }
        """
        try:
            resp = self.client.get(self.ENDPOINT_HISTORICAL %
                                   date.strftime("%Y-%m-%d"),
                                   params={'base': base})
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ExchangeRatesApiClientException(e)
        return resp.json(parse_int=decimal.Decimal,
                         parse_float=decimal.Decimal)
