import pytest

from backtesting.test import GOOG
from backtesting import Strategy, Backtest
from backtesting.lib import crossover
from talib import EMA


class EmaCross(Strategy):
    n1 = 10
    n2 = 30

    def init(self):
        self.ema1 = self.I(EMA, self.data.Close.astype('float'), self.n1)
        self.ema2 = self.I(EMA, self.data.Close.astype('float'), self.n2)

    def next(self):
        if crossover(self.ema1, self.ema2):
            self.position.close()
            self.buy()

        elif crossover(self.ema2, self.ema1):
            self.position.close()
            self.sell()


class EmaCrossLimited(Strategy):
    n1 = 10
    n2 = 30
    fixed_bars = 3
    fixed_return = 3

    def init(self):
        self.ema1 = self.I(EMA, self.data.Close.astype('float'), self.n1)
        self.ema2 = self.I(EMA, self.data.Close.astype('float'), self.n2)

    def next(self):
        if crossover(self.ema1, self.ema2):
            self.position.close()
            self.buy()

        elif crossover(self.ema2, self.ema1):
            self.position.close()
            self.sell()

        if self.position:
            bars_from_last_in = (
                    self.data.index > self.trades[0].entry_time
                    ).sum()
            if bars_from_last_in == self.fixed_bars:
                self.position.close()

        if self.position and abs(self.position.pl_pct) > self.fixed_return:
            self.position.close()


@pytest.fixture
def get_strategy():
    return EmaCross


@pytest.fixture
def sample_stats():
    bt = Backtest(GOOG, EmaCross)
    stats = bt.run()
    return stats
