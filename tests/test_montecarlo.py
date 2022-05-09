from random import seed
from pathlib import Path
import pandas as pd
from tqdm import tqdm

from backtest_tools.montecarlo import montecarlo_a_year, make_report_graph

basepath = Path(__file__).parent

seed(2022)
SIM_TIMES = 1500
INIT_ASSETS = 1_000_000
RUIN_POINT = 800_000


def test_mont_report():
    trades = pd.read_pickle(basepath.parent.joinpath('results/1/test.pickle'))
    ret_list = []
    dd_list = []
    ruin_list = []
    for i in tqdm(range(SIM_TIMES)):
        ret, dd, has_ruin = montecarlo_a_year(trades, INIT_ASSETS, RUIN_POINT)
        ret_list.append(ret)
        dd_list.append(dd)
        ruin_list.append(has_ruin)

    ruin_ratio = pd.Series(ruin_list, dtype='bool').value_counts(normalize=True)
    print(ruin_ratio)
    make_report_graph(ret_list, dd_list, basepath.joinpath('mont_report.html'))
