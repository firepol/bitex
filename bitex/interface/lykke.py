"""Lykke Interface class."""
# pylint: disable=arguments-differ
# Import Built-Ins
import logging

import requests

# Import Homebrew
from bitex.api.REST.lykke import LykkeREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair, format_with
from bitex.formatters import LykkeFormattedResponse


# Init Logging Facilities
log = logging.getLogger(__name__)


class Lykke(RESTInterface):
    """Lykke REST API Interface Class."""

    def __init__(self, **api_kwargs):
        """Initialize the Interface class instance."""
        self.public_api = 'https://public-api.lykke.com/api/'
        super(Lykke, self).__init__('Lykke', LykkeREST(**api_kwargs))

    def _get_supported_pairs(self):
        """Return a list of supported pairs."""
        resp = self.asset_pairs()
        return [pair["Id"] for pair in resp.json()]

    def request(self, verb, endpoint, authenticate=False, **kwargs):
        """Generate a request to the API."""
        return super(Lykke, self).request(verb, endpoint, authenticate=authenticate, **kwargs)

    ###############
    # Basic Methods
    ###############

    # Public Endpoints

    @check_and_format_pair
    @format_with(LykkeFormattedResponse)
    def ticker(self, pair, *args, **kwargs):
        """Return the ticker for the given pair."""
        return requests.request('GET', self.public_api + 'Market/' + pair)

    @check_and_format_pair
    @format_with(LykkeFormattedResponse)
    def order_book(self, pair, *args, **kwargs):
        """Return the order book for the given pair."""
        return requests.request('GET', self.public_api + 'OrderBook/' + pair, params=kwargs)

    @check_and_format_pair
    @format_with(LykkeFormattedResponse)
    def trades(self, pair, *args, **kwargs):
        """Return trades for the given pair."""
        # 'skip' and 'take' are mandatory
        if kwargs.get('skip') is None:
            kwargs.update({'skip': 0})
        if kwargs.get('take') is None:
            kwargs.update({'take': 1000})
        return requests.request('GET', self.public_api + 'Trades/' + pair, params=kwargs)

    # Private Endpoints

    @check_and_format_pair
    @format_with(LykkeFormattedResponse)
    def ask(self, pair, price, size, *args, market=False, **kwargs):
        """Place an ask order."""
        return self._place_order(pair, price, size, 'sell', market=market, **kwargs)

    @check_and_format_pair
    @format_with(LykkeFormattedResponse)
    def bid(self, pair, price, size, *args, market=False, **kwargs):
        """Place a bid order."""
        return self._place_order(pair, price, size, 'buy', market=market, **kwargs)

    def _place_order(self, pair, price, size, side, market=None, **kwargs):
        raise NotImplementedError
        """Place an order with the given parameters."""
        payload = {'amount': size, 'price': price}
        payload.update(kwargs)
        if market:
            return self.request('%s/market/%s/' % (side, pair), authenticate=True, params=payload)
        return self.request('%s/%s/' % (side, pair), authenticate=True, params=payload)

    @format_with(LykkeFormattedResponse)
    def order_status(self, order_id, *args, **kwargs):
        raise NotImplementedError
        """Return the order status for the given order's ID."""
        payload = {'id': order_id}
        payload.update(kwargs)
        return self.request('api/order_status/', authenticate=True, params=payload)

    @format_with(LykkeFormattedResponse)
    def open_orders(self, *args, **kwargs):
        """Return all open orders."""
        return self.orders('InOrderBook', **kwargs)

    @format_with(LykkeFormattedResponse)
    def cancel_order(self, *order_ids, **kwargs):
        raise NotImplementedError
        """Cancel existing order(s) with the given id(s)."""
        results = []
        payload = kwargs
        for oid in order_ids:
            payload.update({'id': oid})
            r = self.request('cancel_order/', authenticate=True, params=payload)
            results.append(r)
        return results if len(results) > 1 else results[0]

    @format_with(LykkeFormattedResponse)
    def wallet(self, *args, **kwargs):
        """Return account's wallet."""
        return self.request('GET', 'Wallets', authenticate=True, params=kwargs)

    ###########################
    # Exchange Specific Methods
    ###########################

    # Public API

    def assets(self):
        """Get a dictionary of all assets."""
        return requests.request('GET', self.public_api + 'Assets/dictionary')

    # HFT API

    def asset_pairs(self):
        """Get all asset pairs."""
        return self.request('GET', 'AssetPairs')

    def orders(self, status=None, **kwargs):
        """
        Get the last orders.

        status (optional):
        - All
        - Open
        - InOrderBook
        - Processing
        - Matched
        - Cancelled
        - Rejected

        take (optional): Default 100; max 500.
        """
        if status:
            kwargs.update({'status': status})
        return self.request('GET', 'Orders', authenticate=True, params=kwargs)

    def trade_history(self, **kwargs):
        """Return past trades of the account."""
        return self.request('GET', 'History/trades', authenticate=True, params=kwargs)
