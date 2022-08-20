import pytest
from backtest_tools.read_zip_data import StockData
from backtest_tools.code_list import CodeList


def test_read_data():
    sd = StockData(code='7203')
    data = sd.read()
    print(data)


def test_read_wrong_data():
    with pytest.raises(FileNotFoundError):
        StockData(code='hoge')


def test_check_len_to_toyota():
    sd = StockData(code='2907')
    print(sd.read())
    diff_ratio = sd.check_len_to_toyota()
    print(diff_ratio)


# def test_check_all_data():
#     code_list = CodeList().read()
#     for code in code_list['コード']:
#         try:
#             sd = StockData(code=code)
#         except FileNotFoundError as e:
#             print(code, ' ', e)

