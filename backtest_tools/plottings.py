from __future__ import annotations

from datetime import date

import pandas as pd
import numpy as np

from bokeh.plotting import figure, save, output_file
from bokeh.plotting.figure import Figure
from bokeh.layouts import gridplot, column
from bokeh.models import ColumnDataSource, CDSView, CustomJS
from bokeh.models import HoverTool, Span, RangeTool
from bokeh.models import BooleanFilter, GroupFilter
from bokeh.events import DoubleTap
from bokeh.models.tools import BoxZoomTool
from bokeh.palettes import Category10_10 as palette


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


class PlotTradeResults:
    """トレードのリターンと保持期間の関係性をプロットする

    ある戦略を特徴付ける指標は、バックテストで得られたトレード履歴における
    リターン分布と保持期間分布である。
    そのリターン分布、保持期間分布の散布状態を、複数の戦略同士、イン期間とアウト期間、
    ブル相場とベア相場、戦略構築時と実際の取引結果などで比較することで、
    戦略の優位性、市場の状態に応じた特性、堅牢性などを評価できると考えている。

    Args:
        title: プロットのタイトル
        bins: サイドにおいた度数分布のビン数

    Attributes:
        bins: 度数分布のビン数
        p: 散布図用のfigure
        ph: 保持期間の度数分布用のfigure
        pv: リターンの度数分布用のfigure
        df_trades: 追加したすべてのトレード履歴

    """

    def __init__(self, title: str, bins: int = 20) -> None:
        self.bins = bins
        self.p = figure(
                title=title,
                tools='pan,wheel_zoom,crosshair',
                width=500,
                height=500,
                x_axis_location='above',
                y_axis_location='left',
                background_fill_color='#fafafa',
                toolbar_location='above',
                active_scroll='wheel_zoom',
                )
        hovertool = HoverTool(
                tooltips=[
                    ('Duration', '@Duration'),
                    ('Return', '@ReturnPct{%0.2f}'),
                ],
                mode='mouse',
                )
        self.p.add_tools(hovertool)
        self.p.yaxis.axis_label = 'リターン'
        self.p.xaxis.axis_label = '日数'

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
                x_axis_location='above',
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

        self.df_trades = None

    def add_record(self, trades: pd.DataFrame, legend: str) -> None:
        """トレード履歴を追加する

        Args:
            trades: トレード履歴(stats._tradesを想定)
            legend: 凡例(識別、色分け用)

        """
        trades['legend'] = legend
        trades['Duration'] = trades['Duration'].dt.days
        self.df_trades = pd.concat([
            self.df_trades,
            trades,
            ])

    def _plot(self) -> None:
        legends = self.df_trades['legend'].unique()
        scatter_source = ColumnDataSource(self.df_trades)
        h_df = self._set_hist_source(self.df_trades['Duration'])
        v_df = self._set_hist_source(self.df_trades['ReturnPct'])

        for i, legend in enumerate(legends):
            self.p.scatter(
                    'Duration',
                    'ReturnPct',
                    source=scatter_source,
                    view=CDSView(
                        source=scatter_source,
                        filters=[GroupFilter(
                            column_name='legend',
                            group=legend,
                            )]
                        ),
                    legend_label=legend,
                    size=12,
                    color=palette[i % 10],
                    alpha=0.4
                    )

            self.ph.scatter(
                    h_df[h_df['legend'] == legend]['x'],
                    h_df[h_df['legend'] == legend]['hist'],
                    color=palette[i % 10],
                    alpha=0.5,
                    size=6,
                    )
            self.ph.line(
                    h_df[h_df['legend'] == legend]['x'],
                    h_df[h_df['legend'] == legend]['hist'],
                    color=palette[i % 10],
                    line_width=4,
                    alpha=0.4,
                    )

            self.pv.scatter(
                    v_df[h_df['legend'] == legend]['hist'],
                    v_df[h_df['legend'] == legend]['x'],
                    color=palette[i % 10],
                    alpha=0.5,
                    size=6,
                    )
            self.pv.line(
                    v_df[h_df['legend'] == legend]['hist'],
                    v_df[h_df['legend'] == legend]['x'],
                    color=palette[i % 10],
                    line_width=4,
                    alpha=0.4,
                    )

    def _set_hist_source(self, sr_line: pd.Series) -> pd.DataFrame:
        range_max = sr_line.max()
        range_min = sr_line.min()

        source_line = None
        legends = self.df_trades['legend'].unique()
        for legend in legends:
            sr = sr_line[self.df_trades['legend'] == legend]
            hist, edge = np.histogram(
                    sr,
                    bins=self.bins,
                    range=(range_min, range_max),
                    )
            mid_point = (edge[:-1] + edge[1:]) / 2
            df_new = pd.DataFrame({
                'x': mid_point,
                'hist': hist,
                'legend': legend,
                })
            source_line = pd.concat([source_line, df_new])
        return source_line

    def save(self, output: str):
        """プロットを保存する

        Args:
            output: 出力するパス、ファイル名を文字列で入力

        """
        self._plot()
        self.p.legend.location = 'top_left'
        self.p.legend.click_policy = 'hide'
        layout = gridplot(
                [[self.p, self.pv], [self.ph, None]],
                merge_tools=False
                )
        output_file(output)
        save(layout)


if __name__ == '__main__':
    pass
