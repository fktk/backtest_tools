from backtest_tools.montecarlo import Montecarlo


def test_mont_report(sample_stats):
    trades = sample_stats._trades

    mont = Montecarlo(trades, 1_000_000., 800_000)
    mont.run(sim_times=2000)
    mont.make_report_graph('tests/mont.html')
