from tqdm import tqdm
from pathlib import Path
import pandas as pd
import numpy as np

from src.read_price import parse_protra_data

basepath = Path(__file__).parent.joinpath('data')


def get_indices():
    df = pd.read_csv(basepath.joinpath('index2.csv'))
    return df


def get_change(data):
    try:
        df_pct = data.pct_change()['Close'] * 100
        df_diff = data.diff()['Close']
        df_concat = pd.concat([df_diff, df_pct], axis=1)
        df_concat.columns = ['diff', 'ratio']
        return df_concat

    except IndexError:
        raise IndexError

    except AttributeError:
        raise AttributeError


def calc_diff():
    df_indices = get_indices()
    df = pd.DataFrame(dict(
        code=[],
        diff=[],
        ratio=[],
    ))
    for index in tqdm(df_indices['index']):
        try:
            df_change = get_change(data=parse_protra_data(index))
            df_change['code'] = index
            df = pd.concat([df, df_change])
        except (IndexError, AttributeError):
            pass

    df = df.query('-35 < ratio < 35')
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()
    df.to_pickle(basepath.joinpath('diff.pickle'))


def get_ranking(query_str='25 < ratio < 35'):
    df = pd.read_pickle(basepath.joinpath('diff.pickle'))
    df = df.query(query_str).sort_values('ratio')
    return df


if __name__ == '__main__':
    # calc_diff()
    get_ranking()
