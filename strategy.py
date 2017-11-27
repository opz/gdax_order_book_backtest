import logging
import math

import pandas as pd

logger = logging.getLogger(__name__)

class Strategy:
    """
    """

    PERIOD = 30

    def __init__(self):
        self.broker = None
        self.order_book_imbalance = []


    def next(self, key, data):
        """
        """

        if self.broker == None:
            raise NotImplementedError('Broker must be added to Strategy')

        delta = 2
        beta = 1

        bid_qty = 0
        for index, row in data[data['type'] == 'b'].iterrows():
            price_diff = abs(row['price'] - self.broker.best_bid)
            price_pct_diff = price_diff / self.broker.best_bid
            bid_qty += row['size'] / (delta * price_pct_diff + beta)

        ask_qty = 0
        for index, row in data[data['type'] == 'a'].iterrows():
            price_diff = abs(row['price'] - self.broker.best_ask)
            price_pct_diff = price_diff / self.broker.best_ask
            ask_qty += row['size'] / (delta * price_pct_diff + beta)

        order_book_imbalance = (bid_qty - ask_qty) / (bid_qty + ask_qty)

        self.order_book_imbalance.append(order_book_imbalance)

        obi_period = len(self.order_book_imbalance) > Strategy.PERIOD
        if obi_period:
            last_period_obi = self.order_book_imbalance[-Strategy.PERIOD:]

            signal = order_book_imbalance

            threshold = pd.DataFrame(last_period_obi).std()[0]
            buy_threshold = threshold * 2
            sell_threshold = -threshold * 2

            if signal > buy_threshold:
                self.broker.buy()
            elif signal < sell_threshold:
                self.broker.sell()


    def metrics(self):
        print(self.broker.accounts)


    def add_broker(self, broker):
        self.broker = broker
