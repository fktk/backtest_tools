from __future__ import annotations
from datetime import date
from typing import Optional

import pandas as pd
from backtesting import Backtest, Strategy
from backtesting._stats import _Stats


def out_of_sample(
    df: pd.DataFrame,
    in_date: tuple[date, date],
    out_date: tuple[date, date],
    MyStrategy: Strategy,
    optimize_params: dict,
    optimize_config: dict,
    backtest_config: Optional[dict] = {'cash': 100_000, 'commission': .002}
) -> tuple[_Stats, _Stats]:
    """アウトオブサンプルテストを一度実行する

    インサンプル期間をつかって戦略のパラメータを最適化し、
    その戦略でアウトオブサンプル期間のバックテストを行う

    Args:
        df: 日々の価格データ
        in_date: インサンプルテストの開始と終了日
        out_date: アウトオブサンプルテストの開始と終了日
        MyStrategy: 戦略クラス インスタンスではない
        optimize_params: 最適化を行うパラメータの範囲
        optimize_config: 最適化の条件 詳しくはbacktesting.py
        backtest_config: バックテストクラス用の設定

    Returns:
        インサンプルテストとアウトオブサンプルテストの結果

    """

    df_in = df.query('@in_date[0] <= index < @in_date[1]')
    bt_in = Backtest(df_in, MyStrategy, **backtest_config)
    stats_in = bt_in.optimize(
        **optimize_params,
        **optimize_config,
    )

    for k, v in stats_in._strategy._params.items():
        setattr(MyStrategy, k, v)

    df_out = df.query('@out_date[0] <= index < @out_date[1]')
    bt_out = Backtest(df_out, MyStrategy, **backtest_config)
    stats_out = bt_out.run()
    return stats_in, stats_out


if __name__ == '__main__':
    pass
