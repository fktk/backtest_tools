import pytest

from backtesting.test import GOOG
from backtesting import Strategy, Backtest
from backtesting.lib import crossover
from talib import EMA


class EmaCross(Strategy):
    n1 = 15
    n2 = 50

    def init(self):
        self.ema1 = self.I(EMA, self.data.Close.astype(float), self.n1)
        self.ema2 = self.I(EMA, self.data.Close.astype(float), self.n2)

    def next(self):
        if crossover(self.ema1, self.ema2):
            self.position.close()
            self.buy()

        elif crossover(self.ema2, self.ema1):
            self.position.close()
            self.sell()


@pytest.fixture
def get_strategy():
    return EmaCross


@pytest.fixture
def sample_stats():
    bt = Backtest(GOOG, EmaCross)
    stats = bt.run()
    return stats
