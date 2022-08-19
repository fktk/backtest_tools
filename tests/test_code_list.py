from pathlib import Path

import pytest

from backtest_tools.code_list import CodeList


def test_read_code_list():
    code_list = CodeList()
    print(code_list.read())
    assert not code_list.read().empty

def test_read_code_list_with_wrong_path():
    with pytest.raises(FileNotFoundError):
        CodeList(srcfile_path=Path('./hoge.xls'))
