from __future__ import annotations

from datetime import date

import pandas as pd
import numpy as np

from bokeh.plotting import figure, save, output_file
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, CDSView, CustomJS
from bokeh.models import HoverTool, Span, BoxAnnotation
from bokeh.models import GroupFilter
from bokeh.models import NumeralTickFormatter
from bokeh.models import Model
from bokeh.events import DoubleTap
from bokeh.palettes import Category10_10 as palette

from backtesting import Backtest, Strategy


class StackCharts:

    def __init__(self):
        self.fig = []

    def add(self,
            data: pd.DataFrame,
            strategy: Strategy,
            title: str | None = None,
            hatch_range: tuple[date | None, date | None] = (None, None)
            ):
        strategy.next = lambda self: False

        bt = Backtest(data, strategy)
        bt.run()

        fig = bt.plot(superimpose=False, open_browser=False)
        for model in fig.select({'type': Model}):
            prev_doc = model.document
            model._document = None
            if prev_doc:
                prev_doc.remove_root(model)

        fig_ohlc = fig.children[0].children[0][0]
        fig_ohlc.height = 200
        fig_ohlc.js_on_event(DoubleTap, CustomJS(
            args=dict(p=fig_ohlc), code='p.reset.emit()'
            ))
        if hatch_range[0] is not None:
            fig_ohlc.add_layout(
                    BoxAnnotation(
                        left=bt._data.index.get_indexer(
                            [hatch_range[0]], method='nearest')[0],
                        right=bt._data.index.get_indexer(
                            [hatch_range[1]], method='nearest')[0],
                        fill_color='red',
                        fill_alpha=0.1,
                        )
                    )
        fig_ohlc.title = title
        self.fig.append(fig)

    def save(self, filename):
        output_file(filename)
        save(gridplot(self.fig, sizing_mode='stretch_width', ncols=1))


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
                    ('エントリー日', '@EntryTime{%F}'),
                    ('足の本数', '@DurationBars 本'),
                    ('リターン', '@ReturnPct{%0.2f}'),
                ],
                mode='mouse',
                formatters={
                    '@EntryTime': 'datetime',
                },
                )
        self.p.add_tools(hovertool)
        self.p.yaxis.axis_label = 'リターン'
        self.p.xaxis.axis_label = '足の本数'
        self.p.xaxis.major_label_text_font_size = '1.1em'
        self.p.yaxis.major_label_text_font_size = '1.1em'
        self.p.yaxis[0].formatter = NumeralTickFormatter(format='0%')
        self.p.add_layout(
                Span(location=0, dimension='width', line_color='red')
                )

        self.ph = figure(
                toolbar_location=None,
                width=self.p.width, height=200,
                x_range=self.p.x_range,
                background_fill_color="#fafafa",
                )
        self.ph.xaxis.axis_label = '足の本数'
        self.ph.xaxis.major_label_text_font_size = '1.1em'
        self.pv = figure(
                toolbar_location=None, width=200, height=self.p.height,
                y_range=self.p.y_range,
                x_axis_location='above',
                y_axis_location='right',
                background_fill_color='#fafafa',
                )
        self.pv.yaxis.axis_label = 'リターン'
        self.pv.yaxis.major_label_text_font_size = '1.1em'
        self.pv.add_layout(
                Span(location=0, dimension='width', line_color='red')
                )
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
        # trades['Duration'] = trades['Duration'].dt.days
        trades['DurationBars'] = trades['ExitBar'] - trades['EntryBar']
        self.df_trades = pd.concat([
            self.df_trades,
            trades,
            ])

    def _plot(self, legend_col: str = 'legend') -> None:
        legends = self.df_trades[legend_col].unique()

        scatter_source = ColumnDataSource(self.df_trades)
        h_df = self._set_hist_source(self.df_trades['DurationBars'], legend_col)
        v_df = self._set_hist_source(self.df_trades['ReturnPct'], legend_col)

        for i, legend in enumerate(legends):
            p = self.p.scatter(
                    'DurationBars',
                    'ReturnPct',
                    source=scatter_source,
                    view=CDSView(
                        source=scatter_source,
                        filters=[GroupFilter(
                            column_name=legend_col,
                            group=legend,
                            )]
                        ),
                    legend_label=legend,
                    size=12,
                    color=palette[i % 10],
                    alpha=0.4
                    )

            ph1 = self.ph.scatter(
                    h_df[h_df[legend_col] == legend]['x'],
                    h_df[h_df[legend_col] == legend]['hist'],
                    color=palette[i % 10],
                    alpha=0.5,
                    size=6,
                    )
            ph2 = self.ph.line(
                    h_df[h_df[legend_col] == legend]['x'],
                    h_df[h_df[legend_col] == legend]['hist'],
                    color=palette[i % 10],
                    line_width=4,
                    alpha=0.4,
                    )

            pv1 = self.pv.scatter(
                    v_df[h_df[legend_col] == legend]['hist'],
                    v_df[h_df[legend_col] == legend]['x'],
                    color=palette[i % 10],
                    alpha=0.5,
                    size=6,
                    )
            pv2 = self.pv.line(
                    v_df[h_df[legend_col] == legend]['hist'],
                    v_df[h_df[legend_col] == legend]['x'],
                    color=palette[i % 10],
                    line_width=4,
                    alpha=0.4,
                    )
            p.js_on_change('visible', CustomJS(
                args=dict(ph1=ph1, ph2=ph2, pv1=pv1, pv2=pv2),
                code="""
                ph1.visible = !(ph1.visible);
                ph2.visible = !(ph2.visible);
                pv1.visible = !(pv1.visible);
                pv2.visible = !(pv2.visible);
                """
                ))

    def _set_hist_source(
            self,
            sr_line: pd.Series,
            legend_col: str = 'legend'
            ) -> pd.DataFrame:
        range_max = sr_line.max()
        range_min = sr_line.min()

        source_line = None
        legends = self.df_trades[legend_col].unique()
        for legend in legends:
            sr = sr_line[self.df_trades[legend_col] == legend]
            hist, edge = np.histogram(
                    sr,
                    bins=self.bins,
                    range=(range_min, range_max),
                    )
            mid_point = (edge[:-1] + edge[1:]) / 2
            df_new = pd.DataFrame({
                'x': mid_point,
                'hist': hist,
                legend_col: legend,
                })
            source_line = pd.concat([source_line, df_new])
        return source_line

    def save(self, output: str, legend_col: str = 'legend'):
        """プロットを保存する

        Args:
            output: 出力するパス、ファイル名を文字列で入力

        """
        self._plot(legend_col)

        self.p.legend.location = 'top_left'
        self.p.legend.click_policy = 'hide'
        self.p.legend.label_text_font_size = '1.2em'

        layout = gridplot(
                [[self.p, self.pv], [self.ph, None]],
                merge_tools=False
                )
        output_file(output)
        save(layout)


if __name__ == '__main__':
    pass
