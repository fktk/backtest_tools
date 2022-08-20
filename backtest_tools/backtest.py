from __future__ import annotations

import os
import warnings
import multiprocessing as mp
from datetime import date
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd
import numpy as np
from tqdm import tqdm
from backtesting import Backtest, Strategy
from backtesting._stats import _Stats

from .utils import cut_not_closed_trades


def out_of_sample(
        df: pd.DataFrame,
        MyStrategy: Strategy,
        in_date: tuple[date, date],
        out_date: tuple[date, date],
        optimize_params: dict,
        backtest_config: dict | None = {'cash': 100_000, 'commission': .002}
        ) -> tuple[_Stats, _Stats]:
    """アウトオブサンプルテストを一度実行する

    インサンプル期間をつかって戦略のパラメータを最適化し、
    そのパラメータでアウトオブサンプル期間のバックテストを行う

    Args:
        df: 日々の価格データ
        MyStrategy: 戦略クラス インスタンスではない
        in_date: インサンプルテストの開始と終了日
        out_date: アウトオブサンプルテストの開始と終了日
        optimize_params: 最適化パラメータ 詳しくはbacktesting.py
        backtest_config: バックテストクラス用の設定

    Returns:
        インサンプルテストとアウトオブサンプルテストの結果

    """
    df_in = df.query('@in_date[0] <= index < @in_date[1]')
    bt_in = Backtest(df_in, MyStrategy, **backtest_config)
    stats_in = bt_in.optimize(**optimize_params)

    df_out = df.query('@out_date[0] <= index < @out_date[1]')
    bt_out = Backtest(df_out, MyStrategy, **backtest_config)
    stats_out = bt_out.run(**stats_in._strategy._params)
    return stats_in, stats_out


def walkforward(
        df: pd.DataFrame,
        MyStrategy: Strategy,
        in_period: float,
        out_period: float,
        optimize_params: dict,
        backtest_config: dict | None = {'cash': 1_000_000, 'commission': .002}
        ) -> pd.DataFrame:
    """ウォークフォワードテストを行う

    入力したデータの日付インデックスから、アウトサンプル期間、インサンプル期間のデータを
    順次取得し、アウトオブサンプルテストを行う。
    インサンプル期間として取得したデータが少なくなった時点でテストを終える。

    Args:
        df: 価格データ
        MyStrategy: 戦略クラス
        in_period: インサンプルの期間を年数で指定する
        out_period: アウトサンプルの期間を年数で指定する
        optimize_params: 最適化パラメータ 詳しくはbacktesting.py
        backtest_config: バックテストクラス用の設定

    Returns:
        テストの結果の概要とトレード履歴

    """
    torelance = 0.9  # インサンプル期間が指定日数のx以下だと、そのデータはテストしない
    output_params = {
        'Start': '開始日',
        'End': '終了日',
        'Exposure Time [%]': '建玉日比率[%]',
        '# Trades': 'トレード回数',
        'Win Rate [%]': '勝率[%]',
        'Best Trade [%]': 'ベストトレード[%]',
        'Worst Trade [%]': 'ワーストトレード[%]',
        'Avg. Trade [%]': '平均トレード[%]',
        'Max. Trade Duration': '最大トレード期間',
        'Avg. Trade Duration': '平均トレード期間',
    }
    results = []
    trades = pd.DataFrame({})

    end_date = df.index[-1]
    check_in_data_period = True
    while check_in_data_period:

        mid_date = end_date - pd.Timedelta(365 * out_period, 'd')
        start_date = mid_date - pd.Timedelta(365 * in_period, 'd')
        in_df = df.query('@start_date < index < @mid_date')
        # インサンプル期間が十分取得できているかを確認する
        check_in_data_period = (
                (in_df.index[-1] - in_df.index[0]) >
                pd.Timedelta(365 * in_period * torelance, 'd')
                )
        if not check_in_data_period:
            break

        _, stats_out = out_of_sample(
                df,
                MyStrategy,
                (start_date, mid_date),
                (mid_date, end_date),
                optimize_params=optimize_params,
                )
        out_bars = len(df.query('@mid_date <= index < @end_date')) - 1
        end_date = mid_date

        # アウトサンプル期間の最後まで持っている玉は除去する
        # queryのみだとビューを返し、その後代入するときにワーニングがでるためcopy()する
        fin_trades = stats_out._trades.query('ExitBar != @out_bars').copy()
        fin_trades['Strategy'] = str(stats_out._strategy)
        trades = pd.concat([trades, fin_trades])

        result = dict()
        for k, v in output_params.items():
            result.update({v: stats_out[k]})

        for k, v in stats_out._strategy._params.items():
            result.update({k: v})

        results.append(result)

    results = pd.DataFrame(results)

    # print(results)
    # print(trades)
    return results, trades


def backtest_for_multiple_data(
        data_name_tpl_lst: list[tuple[pd.DataFrame, str]],
        strategy: Strategy
        ) -> pd.DataFrame:
    """
    多数のデータを同じ戦略で計算する 高速化のためマルチプロセスで計算させている

    Args:
        data_name_tpl_lst: データと識別用の名前をタプルにして、それを多数用意し、リスト化したもの
        strategy: 戦略クラス インスタンスではない

    Returns:
        バックテストのトレード履歴
        バックテスト期間の最後まで保持していたポジションは削除している

    """
    code_batches = list(_batch(data_name_tpl_lst))

    if mp.get_start_method(allow_none=False) == 'fork':
        trades = pd.DataFrame({})
        with ProcessPoolExecutor() as executor:
            futures = [
                    executor.submit(_batch_backtest, b_code_lst, strategy)
                    for b_code_lst in code_batches]

            for future in tqdm(as_completed(futures), total=len(futures)):
                trades = pd.concat([trades, future.result()])

    else:
        if os.name == 'posix':
            warnings.warn(
                    "For multiprocessing support"
                    "set multiprocessing start method to 'fork'.")
        trades = _batch_backtest(data_name_tpl_lst, strategy)

    return trades


def _batch(seq: list):
    n = np.clip(int(len(seq) // (os.cpu_count() or 1)), 1, 300)
    for i in range(0, len(seq), n):
        yield seq[i: i+n]


def _batch_backtest(
        data_name_tpl_lst: list[tuple[pd.DataFrame, str]],
        strategy: Strategy
        ) -> pd.DataFrame:

    trades = pd.DataFrame({})
    for data_name_tpl in tqdm(data_name_tpl_lst):
        data = data_name_tpl[0]
        name = data_name_tpl[1]
        bt = Backtest(data, strategy)
        stats = bt.run()
        trade = cut_not_closed_trades(stats)
        # trade = stats._trades
        trade['name'] = name
        del bt
        trades = pd.concat([trades, trade])
    return trades


if __name__ == '__main__':
    pass
