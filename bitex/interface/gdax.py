"""GDAX Interface class."""
# pylint: disable=abstract-method
# Import Built-Ins
import logging

# Import Third-party
import requests

# Import Homebrew
from bitex.api.REST.gdax import GDAXREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair, format_with
from bitex.formatters.gdax import GDAXFormattedResponse

# Init Logging Facilities
log = logging.getLogger(__name__)


class GDAX(RESTInterface):
    """GDAX Interface class."""

    def __init__(self, **api_kwargs):
        """Initialize Interface class instance."""
        super(GDAX, self).__init__('GDAX', GDAXREST(**api_kwargs))

    def _get_supported_pairs(self):
        r = requests.request('GET', 'https://api.gdax.com/products').json()
        return [x['id'] for x in r]

    # Public Endpoints
    @check_and_format_pair
    @format_with(GDAXFormattedResponse)
    def ticker(self, pair, *args, **kwargs):
        """
        Return the ticker for the given pair.

        :param pair: Str, pair to request data for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'products/%s/ticker' % pair, params=kwargs)

    @check_and_format_pair
    @format_with(GDAXFormattedResponse)
    def order_book(self, pair, *args, **kwargs):
        """
        Return the order book for the given pair.

        :param pair: Str, pair to request data for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'products/%s/book' % pair, params=kwargs)

    @check_and_format_pair
    @format_with(GDAXFormattedResponse)
    def trades(self, pair, *args, **kwargs):
        """
        Return the trades for the given pair.

        :param pair: Str, pair to request data for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'products/%s/trades' % pair, params=kwargs)

    # Private Endpoints

    def _place_order(self, pair, price, size, side, **kwargs):
        params = {'product_id': pair, 'side': side, 'size': size, 'price': price}
        params.update(kwargs)
        return self.request('POST', 'orders', json=params, authenticate=True)

    @check_and_format_pair
    @format_with(GDAXFormattedResponse)
    def ask(self, pair, price, size, *args, **kwargs):
        """
        Place an ask order.

        :param pair: Str, pair to post order for.
        :param price: Float or str, price you'd like to ask.
        :param size: Float or str, amount of currency you'd like to sell.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self._place_order(pair, price, size, 'sell', **kwargs)

    @check_and_format_pair
    @format_with(GDAXFormattedResponse)
    def bid(self, pair, price, size, *args, **kwargs):
        """
        Place a bid order.

        :param pair: Str, pair to post order for.
        :param price: Float or str, price you'd like to bid.
        :param size: Float or str, amount of currency you'd like to buy.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self._place_order(pair, price, size, 'buy', **kwargs)

    @format_with(GDAXFormattedResponse)
    def order_status(self, order_id, *args, **kwargs):
        """
        Return the status of an order with the given id.

        :param order_id: Order ID of the order you'd like to have a status for.
        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'orders/%s' % order_id, authenticate=True, json=kwargs)

    @format_with(GDAXFormattedResponse)
    def open_orders(self, *args, **kwargs):
        """
        Return all open orders.

        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'orders', authenticate=True, json=kwargs)

    @format_with(GDAXFormattedResponse)
    def cancel_order(self, *order_ids, **kwargs):
        """
        Cancel the order(s) with the given id(s).

        :param order_ids: variable amount of order IDs to cancel.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        path = 'orders/%s'
        resps = []
        for oid in order_ids:
            resps.append(self.request('DELETE', path % oid, authenticate=True, json=kwargs))
        return resps if len(resps) > 1 else resps[0]

    @format_with(GDAXFormattedResponse)
    def wallet(self, *args, **kwargs):
        """
        Return the wallet of this account.

        :param args: additional arguments.
        :param kwargs: additional kwargs, passed to requests.Requests() as 'param' kwarg.
        :return: :class:`requests.Response()` object.
        """
        return self.request('GET', 'accounts', authenticate=True, json=kwargs)

    ###########################
    # Exchange Specific Methods
    ###########################

    def account(self, account_id):
        """
        Information for a single account. Use this endpoint when you know the account_id.

        https://docs.gdax.com/#get-an-account
        """
        return self.request('GET', 'accounts/{}'.format(account_id), authenticate=True)

    def account_history(self, account_id, **kwargs):
        """
        List account activity. Account activity either increases or decreases your account balance. Items are paginated
        and sorted latest first. See the Pagination section for retrieving additional entries after the first page.

        https://docs.gdax.com/#get-account-history
        """
        return self.request('GET', 'accounts/{}/ledger'.format(account_id), authenticate=True, json=kwargs)

    def account_holds(self, account_id, **kwargs):
        """
        Holds are placed on an account for any active orders or pending withdraw requests.
        As an order is filled, the hold amount is updated. If an order is canceled, any remaining hold is removed.
        For a withdraw, once it is completed, the hold is removed.

        https://docs.gdax.com/#get-holds
        """
        return self.request('GET', 'accounts/{}/holds'.format(account_id), authenticate=True, json=kwargs)

    def fills(self, **kwargs):
        """
        Get a list of recent fills.

        You can request fills for specific orders or products using query parameters.

        Param	Default	Description
        order_id	all	Limit list of fills to this order_id
        product_id	all	Limit list of fills to this product_id

        https://docs.gdax.com/#list-fills
        """
        return self.request('GET', 'fills', authenticate=True, json=kwargs)

    def deposit_from_payment_method(self, amount, currency, payment_method_id, **kwargs):
        """
        Deposit funds from a payment method. See the Payment Methods section for retrieving your payment methods.

        https://docs.gdax.com/#payment-method
        """
        kwargs.update({'amount': amount, 'currency': currency.upper(), 'payment_method_id': payment_method_id})
        return self.request('POST', 'deposits/payment-method', authenticate=True)

    def deposit_from_coinbase(self, amount, currency, coinbase_account_id, **kwargs):
        """
        Deposit funds from a coinbase account. You can move funds between your Coinbase accounts and your GDAX trading
        accounts within your daily limits. Moving funds between Coinbase and GDAX is instant and free. See the Coinbase
        Accounts section for retrieving your Coinbase accounts.

        https://docs.gdax.com/#coinbase
        """
        kwargs.update({'amount': amount, 'currency': currency.upper(), 'coinbase_account_id': coinbase_account_id})
        return self.request('POST', 'deposits/coinbase-account', authenticate=True)

    def withdraw_to_payment_method(self, amount, currency, payment_method_id, **kwargs):
        """
        Withdraw funds to a payment method. See the Payment Methods section for retrieving your payment methods.

        https://docs.gdax.com/#payment-method47
        """
        kwargs.update({'amount': amount, 'currency': currency.upper(), 'payment_method_id': payment_method_id})
        return self.request('POST', 'withdrawals/payment-method', authenticate=True)

    def withdraw_to_coinbase(self, amount, currency, coinbase_account_id, **kwargs):
        """
        Withdraw funds to a coinbase account. You can move funds between your Coinbase accounts and your GDAX trading
        accounts within your daily limits. Moving funds between Coinbase and GDAX is instant and free.
        See the Coinbase Accounts section for retrieving your Coinbase accounts.

        https://docs.gdax.com/#coinbase48
        """
        kwargs.update({'amount': amount, 'currency': currency.upper(), 'coinbase_account_id': coinbase_account_id})
        return self.request('POST', 'withdrawals/coinbase-account', authenticate=True)

    def withdraw(self, amount, currency, address, address_tag=None, **kwargs):
        """
        Withdraws funds to a crypto address.

        https://docs.gdax.com/#crypto
        """
        kwargs.update({'amount': amount, 'currency': currency.upper(), 'crypto_address': address})
        return self.request('POST', 'withdrawals/crypto', authenticate=True, json=kwargs)

    def payment_methods(self):
        """
        Get a list of your payment methods.

        https://docs.gdax.com/#list-payment-methods
        """
        return self.request('GET', 'payment-methods', authenticate=True)

    def coinbase_accounts(self):
        """
        Get a list of your coinbase accounts.

        https://docs.gdax.com/#list-accounts53
        """
        return self.request('GET', 'coinbase-accounts', authenticate=True)

    def trailing_volume(self):
        """
        This request will return your 30-day trailing volume for all products.
        This is a cached value that’s calculated every day at midnight UTC.

        https://docs.gdax.com/#trailing-volume
        """
        return self.request('GET', 'users/self/trailing-volume', authenticate=True)
