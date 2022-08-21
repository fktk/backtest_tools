from backtest_tools.code_list import CodeList
from backtest_tools.read_zip_data import set_multiple_data_from_codes, read_cache_data
from backtest_tools.backtest import backtest_for_multiple_data
from backtest_tools.plottings import StackCharts
from backtest_tools.montecarlo import Montecarlo
from backtest_tools.plottings import PlotTradeResults


def test_backtest_from_multiple_data(get_strategy):
    TestStrategy = get_strategy

    codes = CodeList().read().head(100)['コード']
    data_name_tpl_lst = set_multiple_data_from_codes(codes)

    results = backtest_for_multiple_data(data_name_tpl_lst, TestStrategy)
    print(results)


def test_backtest_from_cache_data(get_strategy):
    TestStrategy = get_strategy

    data_name_tpl_lst = read_cache_data()

    results = backtest_for_multiple_data(data_name_tpl_lst[:100], TestStrategy)
    print(results)

#     mont = Montecarlo(results, 1_000_000., 800_000,)
#     mont.run(sim_times=5000)
#     mont.make_report_graph('tests/outputs/integrate_mont.html')

#     plot = PlotTradeResults(title='test', bins=30)
#     plot.add_record(results, '3550')
#     plot.save('tests/outputs/integrate_scatter.html')


def test_backtest_and_montecarlo(get_strategy):
    TestStrategy = get_strategy

    data_name_tpl_lst = read_cache_data()

    results = backtest_for_multiple_data(data_name_tpl_lst[:100], TestStrategy)
    print(results)

    mont = Montecarlo(results, 1_000_000_000., 800_000,)
    mont.run(sim_times=5000)
    mont.make_report_graph('tests/outputs/integrate_mont.html')

#     plot = PlotTradeResults(title='test', bins=30)
#     plot.add_record(results, '3550')
#     plot.save('tests/outputs/integrate_scatter.html')

