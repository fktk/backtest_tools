from random import randrange
from datetime import timedelta
import pandas as pd
import numpy as np
from bokeh.plotting import save, figure, output_file
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, CustomJS, Range1d, LinearAxis
from bokeh.models import HoverTool
from bokeh.events import DoubleTap


def montecarlo_a_year(trades, init_assets, ruin_point):
    # ランダムにトレードを選択し、その合算期間が一年を越したところで止める
    num_trades = len(trades)
    term = timedelta(days=0)
    asset_hist = [init_assets]
    has_ruin = False

    while term < timedelta(days=365):
        i = randrange(num_trades)
        term += trades.Duration.iat[i]
        current_asset = asset_hist[-1]
        asset_hist.append(
            current_asset + asset_hist[-1] * trades.ReturnPct.iat[i]
        )

    asset_sr = pd.Series(asset_hist, dtype='float')
    if asset_sr.min() < ruin_point:
        has_ruin = True

    ret = asset_sr.iat[-1] / init_assets - 1.0
    max_dd = (asset_sr / asset_sr.cummax() - 1).min()
    return ret, max_dd, has_ruin


def make_hist(sr: pd.Series, title, bins=50):
    hist, edges = np.histogram(sr, density=True, bins=bins)
    cum = np.cumsum(hist) * (edges[1] - edges[0])
    source = ColumnDataSource(
        {'hist': hist, 'cum': cum, 'left': edges[:-1], 'right': edges[1:]}
    )

    hovertool = HoverTool(
        tooltips=[
            ('区間', '@left{0.00}-@right{0.00}'),
            ('度数', '@hist{0.00}'),
            ('累積', '@cum{0.00}'),
        ],
        mode='vline',
    )

    TOOLS = "pan,crosshair,save"
    p = figure(title=title, tools=TOOLS, background_fill_color='#fafafa')
    p.add_tools(hovertool)
    p.js_on_event(
        DoubleTap, CustomJS(args=dict(p=p), code='p.reset.emit()')
    )
    p.quad(
        source=source,
        top='hist', bottom=0, left='left', right='right',
        fill_color='navy', line_color='white', alpha=0.8
    )
    p.y_range.start = 0

    p.extra_y_ranges = {'累積': Range1d(start=0, end=1)}
    line = p.line(
        source=source,
        x='left', y='cum',
        line_width=4, line_color='tomato', alpha=0.8,
        y_range_name='累積',
    )
    p.add_layout(LinearAxis(y_range_name='累積'), 'right')
    p.hover.renderers = [line]
    return p


def make_report_graph(ret_list, dd_list, filename):
    ret50 = pd.Series(ret_list, dtype='float').median()
    dd50 = pd.Series(dd_list, dtype='float').median()
    p1 = make_hist(pd.Series(ret_list), f'リターンメジアン:{ret50:.3f}', 50)
    p2 = make_hist(pd.Series(dd_list), f'最大ドロップダウンメジアン:{dd50:.3f}', 50)
    output_file(filename)
    save(gridplot([p1, p2], sizing_mode='stretch_width', height=400, ncols=2))


if __name__ == '__main__':
    pass
