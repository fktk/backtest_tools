from datetime import date

from backtesting.test import GOOG

from backtest_tools.backtest import out_of_sample


def test_out_of_sample(get_strategy):
    TestStrategy = get_strategy

    optimize_params = {
        'n1': range(5, 15, 2),
        'n2': range(10, 30, 2),
        'maximize': 'SQN',
        'constraint': lambda param: param.n1 < param.n2,
    }

    backtest_config = {
        'cash': 1_000_000,
        'commission': 0.01,
    }

    in_date = (date(2007, 1, 1), date(2010, 1, 1))
    out_date = (date(2010, 1, 1), date(2015, 1, 1))

    stats_in, stats_out = out_of_sample(
        GOOG, in_date, out_date, TestStrategy, optimize_params, backtest_config
    )
    print(stats_in)
    print(stats_out)
