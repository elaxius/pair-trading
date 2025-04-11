import backtrader as bt
import numpy as np

class PairTradingStrategy(bt.Strategy):
    params = (
        ('n_period', 230),
        ('threshold', 2.25),
        ('palpha', 0.5),
        ('cutoff', 0.6),
        ('take_profit', 0.0),
    )

    def __init__(self):
        self.state = 0  # 1: short A, long B; -1: long A, short B; 0: no position
        self.data_a = self.datas[0]
        self.data_b = self.datas[1]
        self.close_a = self.data_a.close
        self.close_b = self.data_b.close
        self.account_balance = self.broker.get_cash()
        self.open_balance = self.account_balance
        self.threshold_buffer = self.params.threshold/2.0

    def calculate_kfactor(self, close_a, close_b):
        sum_ab = np.sum(close_a * close_b)
        sum_b2 = np.sum(close_b * close_b)
        return sum_ab / sum_b2

    def calculate_zscore(self, spread):
        mean = np.mean(spread)
        std_dev = np.std(spread)
        return (spread[-1] - mean) / std_dev if std_dev > 0 else 0

    def next(self):
        # Update account balance dynamically
        self.account_balance = self.broker.get_cash()

        if len(self.close_a) < self.params.n_period:
            return

        close_a = np.array(self.close_a.get(size=self.params.n_period))
        close_b = np.array(self.close_b.get(size=self.params.n_period))
        kfactor = self.calculate_kfactor(close_a, close_b)
        spread = close_a - kfactor * close_b
        zscore = self.calculate_zscore(spread)

        # Display current metrics
        # print(f"Z-score: {zscore}, K-factor: {kfactor}, State: {self.state}, Balance: {self.account_balance}")

        # Trading logic
        if self.state == 0:  # No position
            if zscore > self.params.threshold and zscore < (self.params.threshold + self.threshold_buffer / 2):
                lot_a = self.account_balance * self.params.palpha
                lot_b = lot_a * kfactor
                self.sell(data=self.data_a, size=lot_a)
                self.buy(data=self.data_b, size=lot_b)
                self.state = 1
            elif zscore < -self.params.threshold and zscore > -self.params.threshold - self.threshold_buffer / 2:
                lot_a = self.account_balance * self.params.palpha
                lot_b = lot_a * kfactor
                self.buy(data=self.data_a, size=lot_a)
                self.sell(data=self.data_b, size=lot_b)
                self.state = -1

        elif self.state == 1:  # Short A, Long B
            if zscore > self.params.threshold + self.threshold_buffer or self.broker.getvalue() < self.params.cutoff * self.open_balance:
                self.close(self.data_a)
                self.close(self.data_b)
                self.state = 0
            elif zscore < -self.params.take_profit:
                self.close(self.data_a)
                self.close(self.data_b)
                self.state = 0

        elif self.state == -1:  # Long A, Short B
            if zscore < -self.params.threshold - self.threshold_buffer or self.broker.getvalue() < self.params.cutoff * self.open_balance:
                self.close(self.data_a)
                self.close(self.data_b)
                self.state = 0
            elif zscore > self.params.take_profit:
                self.close(self.data_a)
                self.close(self.data_b)
                self.state = 0