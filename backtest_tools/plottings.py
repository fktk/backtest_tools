from __future__ import annotations

from datetime import date

import pandas as pd
import numpy as np

from bokeh.plotting import figure, save, output_file
from bokeh.plotting.figure import Figure
from bokeh.layouts import gridplot, column
from bokeh.models import ColumnDataSource, CDSView, CustomJS
from bokeh.models import BooleanFilter, HoverTool, Span, RangeTool
from bokeh.events import DoubleTap
from bokeh.models.tools import BoxZoomTool
from bokeh.transform import factor_cmap


class Candlestick:
    """複数のローソク足グラフを縦に並べる

    Attributes:
        p(list): 複数のFigureを格納しておく

    """

    w = 12 * 60 * 60 * 1000  # half day in ms
    TOOLS = "pan,ywheel_zoom,crosshair,save"
    hovertool: HoverTool = HoverTool(
            tooltips=[
                ('Date', '@index{%F}'),
                ('Open', '@Open'),
                ('Close', '@Close'),
                ('High', '@High'),
                ('Low', '@Low'),
                ('Volume', '@Volume'),
            ],
            formatters={
                '@index': 'datetime',
            },
            mode='vline'
            )

    def __init__(self) -> None:
        self.p = []

    def _make_candle_figure(self) -> tuple[Figure, Figure]:
        """ローソク足と出来高プロット用のFigureを用意する

        Returns: ローソク足と出来高用のFigureのtupleを返す

        """
        p = figure(
                max_width=600, height=200,
                x_axis_type="datetime",
                y_axis_type='log',
                tools=self.TOOLS,
                toolbar_location='below',
                active_scroll='ywheel_zoom',
                )
        p.add_tools(BoxZoomTool(dimensions='width'))
        p.add_tools(self.hovertool)
        p.js_on_event(
                DoubleTap,
                CustomJS(args=dict(p=p), code='p.reset.emit()')
                )

        p2 = figure(
                max_width=600, height=100,
                x_axis_type="datetime",
                x_range=p.x_range,
                tools=p.tools,
                )
        p2.js_on_event(
                DoubleTap,
                CustomJS(args=dict(p2=p2), code='p2.reset.emit()')
                )

        return p, p2

    def add_chart(self, df: pd.DataFrame, date: date, title: str) -> None:
        """ローソク足と出来高グラフを追加する

        ローソク足と出来高を縦にならべて、self.pに追加する
        最終的に追加したself.pを出力する

        Args:
            df: OHLCV形式のデータ 頭文字は大文字
            date: 網掛けする日付け
            title: タイトル

        """
        p, p2 = self._make_candle_figure()
        p.title = title

        p.add_layout(
                Span(
                    location=date,
                    dimension='height',
                    line_color='red',
                    line_dash='solid',
                    line_alpha=0.1,
                    line_width=10,
                    )
                )

        source = ColumnDataSource(data=df)
        inc = df.Close >= df.Open
        view_inc = CDSView(source=source, filters=[BooleanFilter(inc)])
        dec = df.Open > df.Close
        view_dec = CDSView(source=source, filters=[BooleanFilter(dec)])

        p.segment(
                'index', 'High', 'index', 'Low',
                color="black", source=source, line_width=2
                )
        p.vbar(
                'index', self.w, 'Open', 'Close',
                fill_color="red", line_color="black",
                source=source, view=view_inc
                )
        p.vbar(
                'index', self.w, 'Open', 'Close',
                fill_color="blue", line_color="black",
                source=source, view=view_dec
                )
        p2.vbar(
                x='index', top='Volume',
                width=1, fill_color='black', source=source
                )

        self.p.append(column(p, p2))

    def save(self, filename: str) -> None:
        """グラフを出力する

        Args:
            filename: 出力するHTMLファイルの名前

        """
        output_file(filename)
        save(gridplot(self.p, sizing_mode='stretch_width', ncols=1))


def plot_candlestick_with_rangeslider(
        df: pd.DataFrame,
        filename: str
        ) -> None:
    """レンジスライダー付きローソク足グラフを作る

    Args:
        df: OHLCV形式のデータ 頭文字は大文字
        filename: 出力するファイル名

    """
    source = ColumnDataSource(data=df)

    inc = df.Close >= df.Open
    view_inc = CDSView(source=source, filters=[BooleanFilter(inc)])
    dec = df.Open > df.Close
    view_dec = CDSView(source=source, filters=[BooleanFilter(dec)])
    w = 18 * 60 * 60 * 1000  # half day in ms

    TOOLS = "pan,xwheel_zoom,ywheel_zoom,crosshair"
    p = figure(
            height=400, sizing_mode='stretch_width',
            x_axis_type="datetime",
            tools=TOOLS,
            x_range=(df.index.values[0], df.index.values[-1])
            )
    p.grid.grid_line_alpha = 0.3

    p.segment('index', 'High', 'index', 'Low', color="black", source=source)
    r1 = p.vbar(
            'index', w, 'Open', 'Close',
            fill_color="#D5E1DD", line_color="black",
            source=source, view=view_inc
            )
    r2 = p.vbar(
            'index', w, 'Open', 'Close',
            fill_color="#F2583E", line_color="black",
            source=source, view=view_dec
            )
    hovertool = HoverTool(
            tooltips=[
                ('Date', '@index{%F}'),
                ('Open', '@Open'),
                ('Close', '@Close'),
                ('High', '@High'),
                ('Low', '@Low'),
            ],
            formatters={
                '@index': 'datetime',
            },
            mode='vline',
            renderers=[r1, r2]
            )
    p.add_tools(hovertool)

    p.js_on_event(
            DoubleTap,
            CustomJS(args=dict(p=p), code='p.reset.emit()')
            )

    slider = _set_rangeslider_for_p(p, source)

    output_file(filename)
    save(column(p, slider, sizing_mode='stretch_width'))


def _set_rangeslider_for_p(p, source):
    slider = figure(
            height=100, sizing_mode='stretch_width',
            x_axis_type="datetime", y_axis_type=None,
            tools="", toolbar_location=None,
            background_fill_color="#eee"
            )
    slider.ygrid.grid_line_color = None

    range_tool = RangeTool(x_range=p.x_range)
    range_tool.overlay.fill_color = "navy"
    range_tool.overlay.fill_alpha = 0.2

    slider.line('index', 'Close', source=source)
    slider.add_tools(range_tool)
    slider.toolbar.active_multi = range_tool
    return slider


class ScatterWithHistogram:
    """アウトオブサンプルテストのリターンと保持期間の関係性を比較

    アウトオブサンプルテストではイン期間とアウト期間でトレード履歴が得られる
    それぞれのリターンと保持期間をプロットし、比較することで、
    アウト期間のデータがイン期間と同等かを確認する

    Args:
        trades_in: イン期間のトレード履歴
        trades_out: アウト期間のトレード履歴
        output: 出力するファイル名

    """

    def __init__(self) -> None:
        self.p = figure(
                title='インとアウトの比較',
                tools='pan,wheel_zoom,crosshair',
                width=400,
                height=400,
                x_axis_location=None,
                y_axis_location=None,
                background_fill_color='#fafafa',
                toolbar_location='above',
                )
        hovertool = HoverTool(
                tooltips=[
                    ('Duration', '@Duration_date'),
                    ('Return', '@ReturnPct'),
                ],
                mode='mouse',
                )
        self.p.add_tools(hovertool)

        self.ph = figure(
                toolbar_location=None,
                width=self.p.width, height=200,
                x_range=self.p.x_range,
                background_fill_color="#fafafa",
                )
        self.ph.xaxis.axis_label = '日数'
        self.pv = figure(
                toolbar_location=None, width=200, height=self.p.height,
                y_range=self.p.y_range,
                y_axis_location='right',
                background_fill_color='#fafafa',
                )
        self.pv.yaxis.axis_label = 'リターン'
        self.p.js_on_event(
                DoubleTap,
                CustomJS(
                    args=dict(p=self.p, ph=self.ph, pv=self.pv),
                    code='p.reset.emit(); pv.reset.emit(); ph.reset.emit();')
                )

    def add_record(self, trades_in, trades_out):
        self.source = self._set_source(trades_in, trades_out)
        self.hsource = self._set_hist_source(
                trades_in.Duration.dt.days,
                trades_out.Duration.dt.days,
                )

        self.vsource = self._set_hist_source(
                trades_in.ReturnPct,
                trades_out.ReturnPct,
                )

    def _plot(self):
        self.p.scatter(
                'Duration_date',
                'ReturnPct',
                source=self.source,
                size=8,
                color=factor_cmap('name', 'Category10_3', ['In', 'Out']),
                alpha=0.6
                )

        self.ph.quad(
                top='hist', bottom=0, left='left', right='right',
                fill_color=factor_cmap('name', 'Category10_3', ['In', 'Out']),
                line_color='white', alpha=0.5,
                source=self.hsource,
                )

        self.pv.quad(
                right='hist', left=0, bottom='left', top='right',
                fill_color=factor_cmap('name', 'Category10_3', ['In', 'Out']),
                line_color='white', alpha=0.5,
                source=self.vsource,
                )

    def _set_source(self, trades_in, trades_out):
        trades_in.loc[:, 'name'] = 'In'
        trades_out.loc[:, 'name'] = 'Out'
        trades_in.loc[:, 'Duration_date'] = trades_in['Duration'].dt.days
        trades_out.loc[:, 'Duration_date'] = trades_out['Duration'].dt.days
        scatter_data = pd.concat([
            trades_in.loc[:, ['name', 'ReturnPct', 'Duration_date']],
            trades_out.loc[:, ['name', 'ReturnPct', 'Duration_date']],
            ])

        source = ColumnDataSource(data=scatter_data)
        return source

    def _set_hist_source(self, sr_in, sr_out):
        source = ColumnDataSource({
            'hist': [],
            'left': [],
            'right': [],
            'name': [],
            })
        dur_range_max = max(sr_in.max(), sr_out.max())
        dur_range_min = min(sr_in.min(), sr_out.min())

        hist_in, edges_in = np.histogram(
                sr_in, bins=20,
                range=(dur_range_min, dur_range_max),
                )
        hist_out, edges_out = np.histogram(
                sr_out, bins=20,
                range=(dur_range_min, dur_range_max),
                )
        source.stream({
            'hist': hist_in,
            'left': edges_in[:-1],
            'right': edges_in[1:],
            'name': ['In' for i in range(len(hist_in))],
            })
        source.stream({
            'hist': hist_out,
            'left': edges_out[:-1],
            'right': edges_out[1:],
            'name': ['Out' for i in range(len(hist_out))],
            })
        return source

    def save(self, output):
        layout = gridplot(
                [[self.p, self.pv], [self.ph, None]],
                merge_tools=False
                )
        output_file(output)
        save(layout)


if __name__ == '__main__':
    pass
