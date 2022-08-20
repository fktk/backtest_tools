from __future__ import annotations

import pandas as pd
from itertools import product, repeat
from typing import Sequence


def cut_not_closed_trades(stats: pd.DataFrame) -> pd.DataFrame:
    """バックテスト終了時に強制的にクローズしたトレードを削除する

    Args:
        stats: Backtestクラスのバックテスト結果

    Returns:
        バックテスト期間の最終日にクローズしたトレードをカットしたトレード履歴

    """
    last_day = stats.End
    trades_remain = stats._trades[
            pd.to_datetime(stats._trades.ExitTime).dt.date != last_day.date()
            ]
    return trades_remain


def make_optimize_grid(optimize_params: dict) -> list[dict]:
    """複数のパラメータの最適化条件を総当りにする

    Args:
        optimize_params: 最適化のパラメータと条件

    Returns: 最適化用に各パラメータを辞書化して返す

    """
    if 'constraint' in optimize_params.keys():
        constraint = optimize_params.pop('constraint')
    else:
        def constraint(_):
            return True

    def _tuple(x):
        if isinstance(x, Sequence) and not isinstance(x, str):
            return x
        else:
            return (x, )

    class AttrDict(dict):
        def __getattr__(self, item):
            return self[item]

    param_combos = [
            dict(params) for params in (
                AttrDict(params) for params in product(
                    *(zip(repeat(k), _tuple(v)) for k, v in optimize_params.items())
                    ))
            if constraint(params)]

    return param_combos
