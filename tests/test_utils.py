from backtest_tools.utils import cut_not_closed_trades
from backtest_tools.utils import make_optimize_grid


def test_cut_not_closed_trades(sample_stats):
    stats = sample_stats
    cut_not_closed_trades(stats)


def test_make_optimize_grid():
    optimize_params = {
        'n1': range(5, 15, 2),
        'n2': range(10, 30, 2),
        'constraint': lambda param: param.n1 < param.n2,
    }
    params = make_optimize_grid(optimize_params)
    print(params)
