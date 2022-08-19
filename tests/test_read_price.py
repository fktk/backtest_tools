from backtest_tools.read_price import parse_protra_data


def test_parse_protra_data():
    df = parse_protra_data('1001')
    print(df)
    assert df is not None
