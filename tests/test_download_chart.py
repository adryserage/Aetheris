import importlib.util
import xml.dom.minidom
from datetime import date
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "download_chart.py"
spec = importlib.util.spec_from_file_location("download_chart", SCRIPT)
chart = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chart)

ROWS = [
    {"category": "without_mirrors", "date": "2026-11-02", "downloads": 10},
    {"category": "with_mirrors", "date": "2026-11-02", "downloads": 999},
    {"category": "without_mirrors", "date": "2026-11-03", "downloads": 5},
    {"category": "without_mirrors", "date": "2026-11-09", "downloads": 1200},
    {"category": "without_mirrors", "date": "2026-11-12", "downloads": 34},
]


def test_weekly_sums_per_monday_without_mirrors():
    weeks = chart.weekly(ROWS)
    assert list(weeks.items()) == [(date(2026, 11, 2), 15), (date(2026, 11, 9), 1234)]


def test_render_is_valid_svg_with_total_and_partial_week():
    weeks = chart.weekly(ROWS)
    en = chart.render(weeks, "en", date(2026, 11, 12))
    fr = chart.render(weeks, "fr", date(2026, 11, 12))
    xml.dom.minidom.parseString(en)
    xml.dom.minidom.parseString(fr)
    assert "1,249 downloads in 2 weeks" in en
    assert "1 249 téléchargements en 2 semaines" in fr
    assert "current week, in progress" in en and "semaine en cours" in fr


def test_finished_week_is_not_marked_partial():
    weeks = chart.weekly(ROWS[:3])
    assert "in progress" not in chart.render(weeks, "en", date(2026, 11, 12))
