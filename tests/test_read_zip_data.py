import pytest
from backtest_tools.read_zip_data import StockData, cache_all_data
from backtest_tools.read_zip_data import read_cache_data, set_multiple_data_from_codes
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


def test_set_multiple_data():
    codes = CodeList().read().head(20)['コード']
    data_name_tpl_lst = set_multiple_data_from_codes(codes)
    print(data_name_tpl_lst)


def test_cache_all_data():
    cache_all_data()


def test_read_cache_data():
    list_tuple_data = read_cache_data()
    print(len(list_tuple_data))
    print(list_tuple_data[0][0])
    print(list_tuple_data[0][1])


# def test_check_all_data():
#     code_list = CodeList().read()
#     for code in code_list['コード']:
#         try:
#             sd = StockData(code=code)
#         except FileNotFoundError as e:
#             print(code, ' ', e)

