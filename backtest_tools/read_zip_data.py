"""株価をzipファイルから取得するクラスを提供する

Todo:

"""

import os
from pathlib import Path
import zipfile
import re
import pickle
from concurrent.futures import ProcessPoolExecutor, as_completed

from tqdm import tqdm
import pandas as pd
import numpy as np
from pandas.errors import EmptyDataError

from .code_list import CodeList


class StockData:
    """株価を取得する

    Stooqからダウンロードしたzipから株価を読み込む
    取得した株価はpandasのDataFrameで、
    DatetimeIndex,Open,Close,High,Low,Volumeを持ち、
    株式分割による株価は調整済みである。

    Attributes:
        file_path(str): コード番号

    Args:
        code: コード番号

    Raises:
        Exception: コード指定で2つ以上のパスを取得したときに発生
        FileNotFoundError: 指定したコード番号が見つからなかったときに発生

    """

    zip_dir = Path(__file__).parent.joinpath('data/d_jp_txt.zip')

    def __init__(self, code:str) -> None:

        p = re.compile(rf'data/daily/jp/.*/{code}.jp.txt$')
        with zipfile.ZipFile(self.zip_dir) as zip_dir:
            file_path = list(filter(lambda s: p.search(s), zip_dir.namelist()))
            if len(file_path) == 2:
                raise Exception('２つ以上のファイルを読み込んでいる')
            elif len(file_path) == 0:
                raise FileNotFoundError('ファイルなし')
            else:
                self.file_path = file_path[0]

    def read(self) -> pd.DataFrame:
        """株価を実際に取得する

        Returns: 取得した株価

        Raises:
            EmptyDataError: 取得したデータが空の場合に発生

        """

        use_cols = {
                '<DATE>': 'Date',
                '<OPEN>': 'Open',
                '<HIGH>': 'High',
                '<LOW>': 'Low',
                '<CLOSE>': 'Close',
                '<VOL>': 'Volume',
                }
        with zipfile.ZipFile(self.zip_dir) as zip_dir:
            with zip_dir.open(self.file_path) as f:
                data = pd.read_csv(f, usecols=use_cols.keys())

        if data.empty:
            raise EmptyDataError('空のデータです')

        data['<DATE>'] = pd.to_datetime(data['<DATE>'], format='%Y%m%d')
        data = data.rename(columns=use_cols)
        data = data.set_index('Date')

        return data

    def check_len_to_toyota(self) -> float:
        """トヨタの取引日数に対する、取引日数の比率を返す

        Returns: 取引日数の比率

        """
        toyota = StockData('7203').read()

        me = self.read()
        toyota_match_range = toyota.query('''
                @me.index.min() <= index <= @me.index.max()
                ''')
        return len(me) / len(toyota_match_range)


def set_multiple_data_from_codes(codes) -> list[tuple[pd.DataFrame, str]]:

    code_batches = list(_batch(codes))
    
    list_code = []
    list_data = []
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(_read_data, b_codes)
                for b_codes in code_batches]

        for future in tqdm(as_completed(futures), total=len(futures)):
            lst_data, lst_code = future.result()
            list_code.extend(lst_code)
            list_data.extend(lst_data)

    data_name_tpl_lst = list(zip(list_data, list_code))
    return data_name_tpl_lst


def cache_all_data(
        cache_file: Path = Path(__file__).parent.joinpath('data/cache_data.pkl')
        ) -> None:

    codes = CodeList().read()['コード']
    data_name_tpl_lst = set_multiple_data_from_codes(codes)
    with cache_file.open('wb') as p:
        pickle.dump(data_name_tpl_lst, p)


def read_cache_data(
        cache_file: Path = Path(__file__).parent.joinpath('data/cache_data.pkl')
        ) -> list[tuple[pd.DataFrame, str]]:

    with cache_file.open('rb') as p:
        return pickle.load(p)


def _batch(seq: list):
    n = np.clip(int(len(seq) // (os.cpu_count() or 1)), 1, 300)
    for i in range(0, len(seq), n):
        yield seq[i: i+n]


def _read_data(codes) -> tuple[list[pd.DataFrame], list[str]]:
    list_data = []
    list_code = []
    for code in codes:
        try:
            sd = StockData(code)
        except FileNotFoundError as e:
            print(code, e)
            continue

        if sd.check_len_to_toyota() < 0.8:
            print(code, ' 取引日数がトヨタと比べて少ない')
            continue

        list_data.append(sd.read())
        list_code.append(code)
    return list_data, list_code

