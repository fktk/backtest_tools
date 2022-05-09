from datetime import date
from typing import Tuple

import pandas as pd
from backtesting import Backtest, Strategy
from backtesting._stats import _Stats


def out_of_sample(
    df: pd.DataFrame,
    in_date: Tuple[date, date],
    out_date: Tuple[date, date],
    MyStrategy: Strategy,
    optimize_params,
    optimize_config,
    backtest_config={'cash': 100_000, 'commission': .002}
) -> Tuple[_Stats, _Stats]:

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
