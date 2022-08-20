from pathlib import Path

from jinja2 import Template, Environment, FileSystemLoader


def make_report():
    template_dir = Path(__file__).parent.joinpath('template/')
    charts_dir = Path(__file__).parent.parent.joinpath('tests/outputs/charts/')
    report_file = Path(__file__).parent.parent.joinpath('tests/outputs/report.html')

    env = Environment(loader=FileSystemLoader(template_dir, encoding='utf-8'))
    tmpl = env.get_template('report.j2')

    list_charts = [f.stem for f in charts_dir.glob('*html')]
    rendered_html = tmpl.render(list_charts=list_charts)
    with report_file.open('w') as f:
        f.write(rendered_html)
