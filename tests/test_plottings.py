from datetime import date

from backtesting.test import GOOG

from backtest_tools.backtest import out_of_sample
from backtest_tools.plottings import plot_candlestick_with_rangeslider
from backtest_tools.plottings import Candlestick
from backtest_tools.plottings import compare_in_out

from backtest_tools.get_ranking import get_ranking
from backtest_tools.read_price import parse_protra_data


def test_plot_candlestick():
    plot_candlestick_with_rangeslider(GOOG, 'tests/candle.html')


def test_plot_multi_candle():
    df_ranking = get_ranking()[0: 3]

    num = len(df_ranking)

    plot = Candlestick()
    for i, date_idx, code in zip(range(num), df_ranking.index, df_ranking.code):
        df = parse_protra_data(int(code))
        iloc = df.index.get_loc(date_idx)
        df = df.iloc[iloc-20: iloc+10]
        title = str(int(code)) + ' ' + str(date_idx)[0: 10]
        if len(df) == 30:
            plot.add_chart(df, date_idx, title)

    plot.save('tests/charts.html')


def test_compare_in_out():
    df = GOOG
    print(df.info())
    in_date = (date(2006, 1, 1), date(2010, 1, 1))
    out_date = (date(2010, 1, 1), date(2015, 1, 1))

    stats_in, stats_out = out_of_sample(
        df, in_date, out_date, EmaCross, optimize_params, optimize_config
    )

    compare_in_out(stats_in, stats_out)
