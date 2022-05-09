import pytest

from backtesting.test import GOOG


@pytest.fixture()
def sample_data():
    print(GOOG)
    yield GOOG
