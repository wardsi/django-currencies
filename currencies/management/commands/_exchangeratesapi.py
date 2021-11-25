# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from ._exchangeratesapi_client import ExchangeRatesApiClient, ExchangeRatesApiClientException
from ._currencyhandler import BaseHandler


class CurrencyHandler(BaseHandler):
    """
    Currency Handler implements public API:
    name
    endpoint
    get_allcurrencycodes()
    get_currencyname(code)
    get_ratetimestamp(base, code)
    get_ratefactor(base, code)
    """
    name = 'ExchangeRatesApi'

    def __init__(self, *args):
        """Override the init to check for the APP_ID"""
        APP_ID = getattr(settings, "EXCHANGE_RATES_API_KEY", None)
        if not APP_ID:
            raise ImproperlyConfigured(
                "You need to set the 'EXCHANGE_RATES_API_KEY' setting to your exchangeratesapi.io access key")
        self.client = ExchangeRatesApiClient(APP_ID)
        self.endpoint = self.client.ENDPOINT_CURRENCIES
        super(CurrencyHandler, self).__init__(*args)

    _currencies = None
    @property
    def currencies(self):
        if not self._currencies:
            self._currencies = self.client.currencies()
        return self._currencies

    def get_allcurrencycodes(self):
        """Return an iterable of 3 character ISO 4217 currency codes"""
        return self.currencies.keys()

    def get_currencyname(self, code):
        """Return the currency name from the code"""
        return self.currencies[code]


    def check_rates(self, rates, base):
        """Local helper function for validating rates response"""

        if "rates" not in rates:
            raise RuntimeError("%s: 'rates' not found in results" % self.name)
        if "base" not in rates or rates["base"] != base or base not in rates["rates"]:
            self.log(logging.WARNING, "%s: 'base' not found in results", self.name)
        self.rates = rates

    rates = None
    @property
    def base(self):
        """Only access self.base after check_rates has validated rates"""
        return self.rates["base"]

    def get_latestcurrencyrates(self, base):
        """
        Local helper function
        Changing base is only available for paid-for plans, hence we do it ourselves if required
        Default is USD
        """
        if not self.rates:
            try:
                rates = self.client.latest(base=base)
            except ExchangeRatesApiClientException as e:
                base = 'USD'
                if str(e).startswith('403'):
                    rates = self.client.latest(base=base)
                else:
                    raise
            self.check_rates(rates, base)

    def get_ratetimestamp(self, base, code):
        """Return rate timestamp as a datetime/date or None"""
        self.get_latestcurrencyrates(base)
        try:
            return datetime.fromtimestamp(self.rates["timestamp"])
        except KeyError:
            return None

    def get_ratefactor(self, base, code):
        """Return the Decimal currency exchange rate factor of 'code' compared to 1 'base' unit, or RuntimeError"""
        self.get_latestcurrencyrates(base)
        try:
            ratefactor = self.rates["rates"][code]
        except KeyError:
            raise RuntimeError("%s: %s not found" % (self.name, code))

        if base == self.base:
            return ratefactor
        else:
            return self.ratechangebase(ratefactor, self.base, base)
