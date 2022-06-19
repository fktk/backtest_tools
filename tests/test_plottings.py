from backtesting.test import GOOG

from backtest_tools.plottings import plot_candlestick_with_rangeslider
from backtest_tools.plottings import Candlestick
from backtest_tools.plottings import PlotTradeResults


def test_plot_candlestick():
    plot_candlestick_with_rangeslider(GOOG, 'tests/outputs/candle.html')


def test_plot_multi_candle(sample_stats):
    trades = sample_stats._trades.tail(10)

    plot = Candlestick()
    for entry, exit in zip(trades.EntryTime, trades.ExitTime):
        i_entry = GOOG.index.get_loc(entry)
        i_exit = GOOG.index.get_loc(exit)
        df = GOOG.iloc[i_entry: i_exit+1]
        plot.add_chart(df, date=entry.date(), title='google')

    plot.save('tests/outputs/charts.html')


def test_compare_in_out(sample_stats):
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
