from __future__ import annotations
import random
from datetime import timedelta
from tqdm import tqdm
import pandas as pd
import numpy as np
from bokeh.plotting import save, figure, output_file
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, CustomJS, Range1d, LinearAxis
from bokeh.models import HoverTool
from bokeh.events import DoubleTap
from bokeh.plotting.figure import Figure


class Montecarlo:
    """モンテカルロテストを行い、結果をプロットするクラス

    バックテストを行ったときに生成されたトレード履歴を使って、
    モンテカルロ・シミュレーションを行う。
    トレード履歴の結果が各々独立ならば、無作為に抽出したトレードを
    加算した結果の分布は、戦略が取りうる結果の分布である。

    Attributes:
        trades(pd.DataFrame): トレード履歴
        init_assets(float): 初期資産
        ruin_point(float): 破産とする資産の閾値
        ret_list(list[float]): シミュレーション結果 リターンのリスト
        dd_list(list[float]): シミュレーション結果 ドローダウンのリスト
        ruin_list(list[bool]): シミュレーション結果 破産したかのリスト

    """

    def __init__(
        self,
        trades: pd.DataFrame,
        init_assets: float,
        ruin_point: float,
        seed: int = 2022
    ) -> None:
        """テストに使うトレードと初期資産、破産の閾値をセット

        Args:
            trades: バックテストから得られるトレード履歴 _Stats.trades
            init_assets: 初期資産
            ruin_point: 破産とする資産の閾値
            seed: ランダム値を再現するための設定

        """
        random.seed(seed)
        self.trades = trades
        self.init_assets = init_assets
        self.ruin_point = ruin_point

    def _montecarlo_a_year(
        self,
    ) -> tuple[float, float, bool]:
        """一年分のモンテカルロテストを行う

        バックテスト結果からランダムにトレードを選択し、
        そのリターン比率を資産にかけるという操作を一年分繰り返す
        このテストはバックテストの各トレードが独立した結果であることを仮定している

        Returns:
            一年分のシミュレート結果のリターン資産, 最大ドロップダウン, 破産したかのブール値

        """
        num_trades = len(self.trades)
        sum_duration = timedelta(days=0)
        asset_hist = [self.init_assets]
        has_ruin = False

        while sum_duration < timedelta(days=365):
            i = random.randrange(num_trades)
            sum_duration += self.trades.Duration.iat[i]
            current_asset = asset_hist[-1]
            asset_hist.append(
                current_asset + asset_hist[-1] * self.trades.ReturnPct.iat[i]
            )

        sr_asset = pd.Series(asset_hist, dtype='float')
        if sr_asset.min() < self.ruin_point:
            has_ruin = True

        ret = float(sr_asset.iat[-1] / self.init_assets - 1.0)
        max_dd = float((sr_asset / sr_asset.cummax() - 1).min())
        return ret, max_dd, has_ruin

    def run(self, sim_times: int = 1500) -> None:
        """モンテカルロテストを所定回数行う

        _montecarlo_a_year関数を指定回数行い、その結果(リターン,ドロップダウン、破産したかどうか)を
        リストに格納する
        このリストを元にモンテカルロテストの集計やグラフ化を行う

        Args:
            sim_times: シミュレーションの回数 多いほど集計結果が信頼できるが、時間がかかる

        """
        self.ret_list = []
        self.dd_list = []
        self.ruin_list = []
        for i in tqdm(range(sim_times)):
            ret, dd, has_ruin = self._montecarlo_a_year()
            self.ret_list.append(ret)
            self.dd_list.append(dd)
            self.ruin_list.append(has_ruin)

    def make_report_graph(self, filename: str) -> None:
        """モンテカルロテストのレポートグラフを作成する

        runメソッド後にできるリターンリスト、ドロップダウンリストから、
        ヒストグラムとメジアンを計算し、プロットする
        プロットはhtmlファイルを出力する
        リターンとドロップダウンのメジアンの比率は1.5以上はほしい

        Args:
            filename: 出力するグラフのファイル名

        """
        ret50 = pd.Series(self.ret_list, dtype='float').median()
        dd50 = pd.Series(self.dd_list, dtype='float').median()
        p1 = _make_hist(self.ret_list, f'リターンメジアン:{ret50:.3f}', 50)
        p2 = _make_hist(self.dd_list, f'最大ドロップダウンメジアン:{dd50:.3f}', 50)
        output_file(filename)
        save(gridplot([p1, p2], sizing_mode='stretch_width', height=400, ncols=2))


def _make_hist(lst: list[float], title: str, bins: int | None = 50) -> Figure:
    """度数分布と累積度数分布を出力する

    Args:
        lst: モンテカルロテストで得られたリターンやドロップダウンのリストを入力
        title: メジアンをタイトルにすると、結果がひと目でわかる
        bins: ヒストグラムのビン数

    Returns:
        bokehのFigureを返す これを返却先でsaveする

    """
    hist, edges = np.histogram(lst, density=True, bins=bins)
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


if __name__ == '__main__':
    pass
