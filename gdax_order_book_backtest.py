#!/usr/bin/env python3

import csv
import logging
import os

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import lag_plot, autocorrelation_plot
from statsmodels.tsa.stattools import acf

from strategy import Strategy
from broker import Broker

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class GDAXOrderBookBacktest:
    """
    """

    def __init__(self):
        self.data = None
        self.strategies = []
        self.broker = Broker()


    def add_strategy(self, strategy):
        strategy.add_broker(self.broker)
        self.strategies.append(strategy)


    def load_csv_directory(self, directory):
        """
        """

        logger.info('Loading CSV data from {}...'.format(directory))

        directory_enc = os.fsencode(directory)

        csv_names = ('datetime', 'type', 'price', 'size', 'num-orders')

        filenames = sorted(os.listdir(directory_enc))

        data_list = []

        for filename in filenames:
            file_path_enc = os.path.join(directory_enc, filename)
            file_path = os.fsdecode(file_path_enc)

            data = pd.read_csv(file_path, header=None, names=csv_names)
            data_list.append(data)

            logger.info('Read {}'.format(filename))

        self.data = pd.concat(data_list, ignore_index=True)


    def run(self):
        """
        """

        # Group data so strategies see the full order book in a give moment
        grouped_data = self.data.groupby('datetime')

        logger.info('Running strategies...')

        # Run strategies on data
        for key, item in grouped_data:
            data = grouped_data.get_group(key)

            self.broker.next(key, data)

            for strategy in self.strategies:
                strategy.next(key, data)

        logger.info('Calculating metrics...')

        # Calculate strategy metrics
        for strategy in self.strategies:
            strategy.metrics()


    def plot(self):
        """
        """

        data_plot = self.data

        data_plot_b = data_plot.loc[data_plot['type'] == 'b']
        data_plot_b = data_plot_b.groupby('datetime')['price'].max()
        data_plot_b = data_plot_b.to_frame('Best Bid')

        data_plot = data_plot_b

        account_df = pd.DataFrame.from_records(
            self.broker.account_value,
            index='datetime',
            columns=['datetime', 'Account Value']
        )

        data_plot = data_plot.join(account_df, how='left')
        data_plot = data_plot.interpolate(method='time')

        fig, axes = plt.subplots(nrows=2)

        data_plot['Best Bid'].plot(ax=axes[0])
        data_plot['Account Value'].plot(ax=axes[1])

        first_best_bid = data_plot['Best Bid'].head(1)
        first_best_bid_xy = (first_best_bid.index[0], first_best_bid[0],)
        axes[0].annotate('{}'.format(first_best_bid[0]), first_best_bid_xy)

        last_best_bid = data_plot['Best Bid'].tail(1)
        last_best_bid_xy = (last_best_bid.index[0], last_best_bid[0],)
        axes[0].annotate('{}'.format(last_best_bid[0]), last_best_bid_xy)

        first_account = data_plot['Account Value'].head(1)
        first_account_xy = (first_account.index[0], first_account[0],)
        axes[1].annotate('{}'.format(first_account[0]), first_account_xy)

        last_account = data_plot['Account Value'].tail(1)
        last_account_xy = (last_account.index[0], last_account[0],)
        axes[1].annotate('{}'.format(last_account[0]), last_account_xy)

        plt.show()


if __name__ == '__main__':
    backtest = GDAXOrderBookBacktest()

    strategy = Strategy()
    backtest.add_strategy(strategy)

    backtest.broker.set_account_balance(Broker.USD_ACCOUNT, 1000)

    backtest.load_csv_directory('data/BTC-USD')

    backtest.run()

    backtest.plot()
