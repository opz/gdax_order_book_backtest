import logging
import math
from random import randint

from dateutil import parser

logger = logging.getLogger(__name__)

class Order:
    BUY_ORDER = 'buy'
    SELL_ORDER = 'sell'

    def __init__(self):
        self.delay = 0
        self.type = None


class Broker:
    """
    """

    USD_ACCOUNT = 'USD'
    BTC_ACCOUNT = 'BTC'

    DELAY = 1

    FEE = 0

    def __init__(self):
        self.current_datetime = None
        self.best_bid = math.inf
        self.best_ask = 0

        self.accounts = {
            Broker.USD_ACCOUNT: 0,
            Broker.BTC_ACCOUNT: 0,
        }

        self.account_value = []

        self.orders = []


    def set_account_balance(self, account, balance):
        self.accounts[account] = balance


    def _record_account_balance(self):
            account_value = (
                self.current_datetime,
                self.accounts[Broker.USD_ACCOUNT],
            )
            self.account_value.append(account_value)


    def next(self, key, data):
        """
        """

        self.current_datetime = parser.parse(key)
        self.current_datetime = self.current_datetime.replace(tzinfo=None)
        self.best_bid = data[data['type'] == 'b']['price'].max()
        self.best_ask = data[data['type'] == 'a']['price'].min()

        if not self.account_value:
            self._record_account_balance()

        for order in self.orders:
            if order.delay == 0:
                if order.type == Order.BUY_ORDER:
                    self.execute_buy()
                elif order.type == Order.SELL_ORDER:
                    self.execute_sell()

            order.delay -= 1

        self.orders = [order for order in self.orders if order.delay == 0]


    def execute_buy(self):
        """
        """

        usd_balance = self.accounts[Broker.USD_ACCOUNT]

        if usd_balance > 0:
            logger.info('BUY @ {}'.format(self.best_bid))

            btc_balance = self.accounts[Broker.BTC_ACCOUNT]
            btc_balance += usd_balance / self.best_bid
            self.set_account_balance(Broker.USD_ACCOUNT, 0)

            fee = btc_balance * Broker.FEE
            self.set_account_balance(Broker.BTC_ACCOUNT, btc_balance - fee)


    def execute_sell(self):
        """
        """

        btc_balance = self.accounts[Broker.BTC_ACCOUNT]

        if btc_balance > 0:
            logger.info('SELL @ {}'.format(self.best_ask))

            usd_balance = self.accounts[Broker.USD_ACCOUNT]
            usd_balance += btc_balance * self.best_ask
            self.set_account_balance(Broker.BTC_ACCOUNT, 0)

            fee = usd_balance * Broker.FEE
            self.set_account_balance(Broker.USD_ACCOUNT, usd_balance - fee)

            self._record_account_balance()


    def buy(self):
        """
        """

        order = Order()
        order.delay = randint(0, Broker.DELAY)
        order.type = Order.BUY_ORDER
        self.orders.append(order)


    def sell(self):
        """
        """

        order = Order()
        order.delay = randint(0, Broker.DELAY)
        order.type = Order.SELL_ORDER
        self.orders.append(order)
