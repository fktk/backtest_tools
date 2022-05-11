from datetime import date

from tqdm import tqdm
import pandas as pd

from backtest_tools.backtest import out_of_sample
from backtest_tools.read_price import parse_protra_data
from backtest_tools.get_ranking import get_indices


def test_out_of_sample(sample_data, EmaCross):
    optimize_params = {
        'n1': range(5, 15, 2),
        'n2': range(10, 30, 2),
    }

    optimize_config = {
        'maximize': 'SQN',
        'constraint': lambda param: param.n1 < param.n2,
    }

    df = sample_data
    in_date = (date(2006, 1, 1), date(2010, 1, 1))
    out_date = (date(2010, 1, 1), date(2015, 1, 1))

    stats_in, stats_out = out_of_sample(
        df, in_date, out_date, EmaCross, optimize_params, optimize_config
    )
    print(stats_out)


def test_out_of_sample_multi_codes():
    output_params = {
        'Start': '開始日',
        'End': '終了日',
        'Duration': '期間',
        'Exposure Time [%]': '建玉日比率[%]',
        'Return [%]': 'リターン[%]',
        'Return (Ann.) [%]': '年率リターン[%]',
        'Max. Drawdown [%]': '最大ドローダウン[%]',
        'Max. Drawdown Duration': '最大ドローダウン期間',
        '# Trades': 'トレード回数',
        'Win Rate [%]': '勝率[%]',
        'Best Trade [%]': 'ベストトレード[%]',
        'Worst Trade [%]': 'ワーストトレード[%]',
        'Avg. Trade [%]': '平均トレード[%]',
        'Max. Trade Duration': '最大トレード期間',
        'Avg. Trade Duration': '平均トレード期間',
        'Profit Factor': 'プロフィットファクター',
        'SQN': 'SQN',
    }

    codes = get_indices()
    in_date = (date(2015, 1, 1), date(2020, 1, 1))
    out_date = (date(2020, 1, 1), date(2021, 1, 1))
    results = []
    trades = pd.DataFrame({})

    for code in tqdm(codes.tail(3)['index']):
        result = dict()
        df = parse_protra_data(code)

        try:
            stats_in, stats_out = out_of_sample(
                df, in_date, out_date, EmaCross, optimize_params, optimize_config
            )
            result.update(stats_in._strategy._params.items())
            for k, v in output_params.items():
                result.update({v: stats_out[k]})
            results.append(result)

            stats_out._trades['code'] = code
            trades = pd.concat([trades, stats_out._trades])
        except ValueError as e:
            print(e)
        except OverflowError as e:
            print(e)

    results = pd.DataFrame(results)
    print(results)
    print(trades)
