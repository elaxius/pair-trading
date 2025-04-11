import backtrader as bt
import numpy as np
import pandas as pd
import yfinance as yf
import backtrader.feeds as btfeeds
import backtrader.analyzers as btanalyzers
from PairTradingStrategy import PairTradingStrategy

# Backtesting Setup
if __name__ == '__main__':

    cerebro = bt.Cerebro()
    # Fetch data from Yahoo Finance
    # Fetch data from Yahoo Finance and preprocess
    def fetch_yahoo_data(ticker):
        data = yf.download(ticker, start="2010-01-01", end="2023-12-31")

        # Remove multi-level column names
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Ensure the data has the correct structure for Backtrader
        data = data.rename(columns={
            'Adj Close': 'close',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Volume': 'volume'
        })

        # Drop unnecessary columns if any
        data = data[['open', 'high', 'low', 'close', 'volume']]

        # Remove timezone information from the index
        data.index = data.index.tz_localize(None)

        return bt.feeds.PandasData(dataname=data)


    data_a = fetch_yahoo_data('AUDUSD=X')
    data_b = fetch_yahoo_data('NZDUSD=X')

    cerebro.adddata(data_a)
    cerebro.adddata(data_b)

    # Add strategy
    cerebro.addstrategy(PairTradingStrategy)

    # Set broker parameters
    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.001)

    # Run backtest
    print("Starting Portfolio Value: ", cerebro.broker.getvalue())
    results = cerebro.run()
    print("Ending Portfolio Value: ", cerebro.broker.getvalue())
