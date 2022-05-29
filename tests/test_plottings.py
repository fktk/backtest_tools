from backtesting.test import GOOG

from backtest_tools.plottings import plot_candlestick_with_rangeslider
from backtest_tools.plottings import Candlestick
from backtest_tools.plottings import ScatterWithHistogram


def test_plot_candlestick():
    plot_candlestick_with_rangeslider(GOOG, 'tests/candle.html')


def test_plot_multi_candle(sample_stats):
    trades = sample_stats._trades.tail(10)

    plot = Candlestick()
    for entry, exit in zip(trades.EntryTime, trades.ExitTime):
        i_entry = GOOG.index.get_loc(entry)
        i_exit = GOOG.index.get_loc(exit)
        df = GOOG.iloc[i_entry: i_exit+1]
        plot.add_chart(df, date=entry.date(), title='google')

    plot.save('tests/charts.html')


def test_compare_in_out(sample_stats):
    trades = sample_stats._trades
    trades_in = trades.sample(frac=0.7, random_state=2022)
    trades_out = trades.query('index not in @trades_in.index')

    plot = ScatterWithHistogram()
    plot.add_record(trades_in, trades_out)
    plot.save('tests/hist.html')
    # print(dir(plot.p))
