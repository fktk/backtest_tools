import pytest

from backtesting.test import GOOG
from backtesting import Strategy
from backtesting.lib import crossover
from talib import EMA


@pytest.fixture
def sample_data():
    return GOOG


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


@pytest.fixture
def get_strategy():
    return EmaCross
