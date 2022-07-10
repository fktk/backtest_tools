from datetime import date

from backtesting.test import GOOG

from backtest_tools.backtest import out_of_sample
from backtest_tools.backtest import walkforward
from backtest_tools.backtest import backtest_for_multiple_data


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
        GOOG, TestStrategy, in_date, out_date, optimize_params, backtest_config
    )
    print(stats_in._strategy)
    print(stats_out._strategy)


def test_walkforward(get_strategy):
    TestStrategy = get_strategy
    optimize_params = {
        'n1': range(5, 16, 5),
        'n2': range(10, 31, 5),
        'maximize': 'SQN',
        'constraint': lambda param: param.n1 < param.n2,
    }
    walkforward(GOOG, TestStrategy, 3, 1, optimize_params)


def test_backtest_for_multiple_data(get_strategy):
    data_list = [GOOG for _ in range(200)]
    code_lst = list(range(200))
    data_name_tpl_lst = list(zip(data_list, code_lst))
    TestStrategy = get_strategy
    results = backtest_for_multiple_data(data_name_tpl_lst, TestStrategy)
    print(results)
