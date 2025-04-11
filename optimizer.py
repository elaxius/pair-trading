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
    # cerebro.addstrategy(PairTradingStrategy)

    # Add strategy with optimization
    cerebro.optstrategy(
        PairTradingStrategy,
        n_period=range(100, 365, 10),
        threshold=np.arange(1.0, 3.0, 0.1),
        cutoff=np.arange(0.1, 1, 0.1)
    )

    # Set broker parameters
    cerebro.broker.setcash(10000)
    cerebro.broker.setcommission(commission=0.001)

    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(btanalyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(btanalyzers.Returns, _name="returns")

    # Run backtest
    results = cerebro.run(maxcpus=1)  # Run on a single CPU

    par_list = [[
                x[0].params.n_period,
                x[0].params.threshold,
                x[0].params.cutoff,
                x[0].analyzers.returns.get_analysis()['rnorm100'],
                x[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
                x[0].analyzers.sharpe.get_analysis()['sharperatio']] for x in results]

    # Find the best strategy

    par_df = pd.DataFrame(par_list, columns=['n_period','threshold', 'cutoff', 'return','drawdown','sharpe'])
    print(par_df)
    par_df.to_csv('output.csv')
