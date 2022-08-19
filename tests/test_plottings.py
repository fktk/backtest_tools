from backtesting.test import GOOG
from datetime import date

from backtest_tools.plottings import PlotTradeResults
from backtest_tools.plottings import StackCharts
from backtest_tools.read_zip_data import StockData


def test_result_plot(sample_stats):
    trades = sample_stats._trades
    trades_in = trades.sample(frac=0.5, random_state=2022).copy()
    trades = trades.query('index not in @trades_in.index').copy()
    trades_mid = trades.sample(frac=0.5, random_state=2022).copy()
    trades_out = trades.query('index not in @trades_mid.index').copy()
    print(trades.info())

    plot = PlotTradeResults(title='test', bins=15)
    plot.add_record(trades_in, 'in')
    plot.add_record(trades_mid, 'mid')
    plot.add_record(trades_out, 'out')
    plot.save('tests/outputs/hist.html')


def test_stack_charts(get_strategy):
    sd = StockData('7201')
    data = sd.read()
    MyStrategy = get_strategy
    charts = StackCharts()
    charts.add(
            data.query('@date(2005, 4, 1) <= index < @date(2005, 8, 1)'),
            MyStrategy,
            title='7201',
            hatch_range=(date(2005, 6, 1), date(2005, 7, 1))
            )
    charts.add(
            data.query('@date(2006, 4, 1) <= index < @date(2008, 8, 1)'),
            MyStrategy,
            title='7201',
            )
    sd = StockData('7203')
    data = sd.read()
    charts.add(
            data.query('@date(2006, 4, 1) <= index < @date(2008, 8, 1)'),
            MyStrategy,
            title='7203',
            hatch_range=(date(2005, 6, 1), date(2007, 7, 1))
            )
    charts.save(filename='tests/outputs/stack.html')
