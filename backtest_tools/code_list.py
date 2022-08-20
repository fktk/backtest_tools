"""株式リストを扱うクラスを提供する"""

import pandas as pd
from pathlib import Path


class CodeList:
    """株式リストを扱う

    株式リストはJPXのサイトで提供されており、
    コード番号、銘柄名、市場・商品区分、業種区分、規模区分がリストされている。

    Attributes:
        default_src(Path): リストデータ(Excel)のパスの初期値
        srcfile_path(Path): リストデータのパス

    Args:
        srcfile_path: リストデータのパス

    Raises:
        FileNotFoundError: リストファイルがないときに発生

    """

    default_src = Path(__file__).parent.joinpath(
            'data/data_j.xls')

    def __init__(
            self,
            srcfile_path: Path = default_src,
            ):

        if not srcfile_path.exists():
            raise FileNotFoundError

        self.srcfile_path = srcfile_path

    def read(self) -> pd.DataFrame:
        """リストファイルを読み込む

        Returns:
            株式コードのリスト
        """

        lst_code = pd.read_excel(self.srcfile_path, sheet_name='Sheet1')
        lst_code = lst_code.astype(str)
        return lst_code
