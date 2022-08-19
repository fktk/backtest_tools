import pytest
from backtest_tools.read_zip_data import StockData


def test_read_data():
    sd = StockData(code='7203')
    data = sd.read()
    print(data)

def test_fetch_wrong_data():
    with pytest.raises(FileNotFoundError):
        StockData(code='hoge')
