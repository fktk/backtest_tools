from backtest_tools.code_list import CodeList
from backtest_tools.read_zip_data import StockData
from backtest_tools.backtest import backtest_for_multiple_data
from backtest_tools.plottings import StackCharts
from backtest_tools.montecarlo import Montecarlo
from backtest_tools.plottings import PlotTradeResults

def test_backtest_for_multiple_data(get_strategy):
    TestStrategy = get_strategy

    origin_list = CodeList().read()
    # print(origin_list['33業種コード'].unique())
    industry_filtered_list = origin_list[origin_list['33業種コード']=='3550']
    
    code_list = []
    data_list = []
    for code in industry_filtered_list['コード']:
        try:
            sd = StockData(code)
        except FileNotFoundError as e:
            print(code, e)
        if sd.check_len_to_toyota() < 0.8:
            continue
        data = sd.read()
        code_list.append(code)
        data_list.append(data)

        charts = StackCharts()
        charts.add(
                data,
                TestStrategy,
                title=code,
                )
        charts.save(filename=f'tests/outputs/charts/{code}.html')

    data_name_tpl_lst = list(zip(data_list, code_list))
    results = backtest_for_multiple_data(data_name_tpl_lst, TestStrategy)
    print(results)

    mont = Montecarlo(results, 1_000_000., 800_000,)
    mont.run(sim_times=5000)
    mont.make_report_graph('tests/outputs/integrate_mont.html')

    plot = PlotTradeResults(title='test', bins=30)
    plot.add_record(results, '3550')
    plot.save('tests/outputs/integrate_scatter.html')

