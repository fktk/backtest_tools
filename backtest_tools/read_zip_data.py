"""株価をzipファイルから取得するクラスを提供する

Todo:

"""

from pathlib import Path
import zipfile
import re

import pandas as pd
from pandas.errors import EmptyDataError


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


    def check_len_to_toyota(self):
        toyota = StockData('7203').read()

        me = self.read()
        toyota_match_range = toyota.query('''
                @me.index.min() <= index <= @me.index.max()
                ''')
        return len(me) / len(toyota_match_range)
