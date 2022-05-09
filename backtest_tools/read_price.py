import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

basepath = Path(__file__).parent.joinpath('data/price')


def protra_date(n):
    """protra価格データの数値を日付に変換する
    protraが保存している価格データの日付はC#のDateTimeに渡す引数を日数に変換
    したものである。これは西暦1年1月1日の経過日数であるためUNIX Timestampの
    1970年1月1日に変換した上でdatetime.datetime()に値を渡し返却する。
    Args:
        n (int): protra価格データの日付に対応する数値
    Returns:
        datetime.datetime: 対応する日付
    """
    epoch_19700101 = 719162 + 9. / 24
    return datetime.fromtimestamp((n - epoch_19700101) * 86400.)


def parse_protra_data(code):
    """Protra価格データをパースする
    protraが保存している価格データをパースして、pandas.DataFrameで返却する。
    Args:
        code (str): コード

    Returns:
        pandas.DataFrame: 価格データ
    """
    dir = str(code)[0]
    path = Path(basepath).joinpath(dir).joinpath(str(code))
    if not path.exists():
        return None
    record_dtype = np.dtype([
        ('date', '<i4'),
        ('open', '<i4'),
        ('high', '<i4'),
        ('low', '<i4'),
        ('close', '<i4'),
        ('volume', '<f8')
    ])
    prices = np.fromfile(path, dtype=record_dtype)
    df = pd.DataFrame(data=[[
        protra_date(price['date']),
        price['open'],
        price['high'],
        price['low'],
        price['close'],
        price['volume']] for price in prices],
        columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df.set_index('Date', inplace=True)
    return df


if __name__ == '__main__':
    pass
