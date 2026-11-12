"""Draw the README download chart (downloads.en.svg, downloads.fr.svg) from pypistats.org.

Usage: python scripts/download_chart.py [output_dir]

pypistats keeps about 180 days of daily PyPI downloads. The chart sums them per week,
without mirrors. The download-chart workflow runs this every day and publishes the files
on the `stats` branch, which README.md and README.fr.md load. A failed fetch exits with
code 1 and writes nothing, so the last published chart stays in place.
"""

import json
import sys
import urllib.request
from collections import OrderedDict
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

PACKAGE = "adryserage-aetheris"
API = f"https://pypistats.org/api/packages/{PACKAGE}/overall?mirrors=false"

CANVAS = "#F5F7FA"
INK = "#1F2933"
MUTED = "#52606D"
GRID = "#D9DEE3"
ACCENT = "#0F6E8C"
PARTIAL = "#9CCAD8"
SANS = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"

WIDTH, HEIGHT = 760, 300
LEFT, RIGHT, TOP, BOTTOM = 56, 24, 70, 44

TEXT = {
    "en": {
        "title": "PyPI downloads per week",
        "summary": "{total} downloads in {weeks} weeks, without mirrors. Updated {updated}.",
        "partial": "current week, in progress",
        "months": "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(),
        "thousands": ",",
    },
    "fr": {
        "title": "Téléchargements PyPI par semaine",
        "summary": "{total} téléchargements en {weeks} semaines, sans les miroirs. Mis à jour le {updated}.",
        "partial": "semaine en cours",
        "months": "janv. févr. mars avr. mai juin juil. août sept. oct. nov. déc.".split(),
        "thousands": " ",
    },
}


def fetch() -> list[dict]:
    request = urllib.request.Request(API, headers={"User-Agent": "aetheris-download-chart"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["data"]


def weekly(rows: list[dict]) -> "OrderedDict[date, int]":
    """Downloads summed per ISO week, keyed by the Monday, oldest first."""
    weeks: "OrderedDict[date, int]" = OrderedDict()
    for row in sorted(rows, key=lambda r: r["date"]):
        if row.get("category") != "without_mirrors":
            continue
        day = date.fromisoformat(row["date"])
        monday = day - timedelta(days=day.weekday())
        weeks[monday] = weeks.get(monday, 0) + int(row["downloads"])
    return weeks


def _number(value: int, sep: str) -> str:
    return f"{value:,}".replace(",", sep)


def _step(peak: int) -> int:
    for step in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000):
        if peak / step <= 4:
            return step
    return 10 ** len(str(peak))


def render(weeks: "OrderedDict[date, int]", lang: str, updated: date) -> str:
    text = TEXT[lang]
    sep = text["thousands"]
    mondays = list(weeks)
    counts = list(weeks.values())
    partial = bool(mondays) and updated < mondays[-1] + timedelta(days=6)
    step = _step(max(counts, default=1) or 1)
    top = step * max(1, -(-max(counts, default=1) // step))
    plot_w, plot_h = WIDTH - LEFT - RIGHT, HEIGHT - TOP - BOTTOM
    slot = plot_w / max(len(counts), 1)
    bar = max(slot * 0.7, 1.0)

    def y_of(value: float) -> float:
        return TOP + plot_h - plot_h * value / top

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="{escape(text["title"])}">',
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="{CANVAS}"/>',
        f'<text x="{LEFT}" y="32" font-family="{SANS}" font-size="17" font-weight="600" '
        f'fill="{INK}">{escape(text["title"])}</text>',
    ]
    summary = text["summary"].format(
        total=_number(sum(counts), sep), weeks=len(counts), updated=updated.isoformat()
    )
    out.append(
        f'<text x="{LEFT}" y="52" font-family="{SANS}" font-size="12" fill="{MUTED}">'
        f"{escape(summary)}</text>"
    )
    for tick in range(0, top + 1, step):
        y = y_of(tick)
        out.append(
            f'<line x1="{LEFT}" y1="{y:.1f}" x2="{WIDTH - RIGHT}" y2="{y:.1f}" '
            f'stroke="{GRID}" stroke-width="1"/>'
        )
        out.append(
            f'<text x="{LEFT - 8}" y="{y + 4:.1f}" text-anchor="end" font-family="{SANS}" '
            f'font-size="11" fill="{MUTED}">{_number(tick, sep)}</text>'
        )
    last_month = None
    for i, (monday, count) in enumerate(zip(mondays, counts)):
        x = LEFT + i * slot + (slot - bar) / 2
        y = y_of(count)
        is_partial = partial and i == len(counts) - 1
        fill = PARTIAL if is_partial else ACCENT
        out.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar:.1f}" height="{TOP + plot_h - y:.1f}" '
            f'rx="2" fill="{fill}"><title>{monday.isoformat()}: {_number(count, sep)}</title></rect>'
        )
        if monday.month != last_month:
            last_month = monday.month
            label = text["months"][monday.month - 1]
            if monday.month == 1 or i == 0:
                label += f" {monday.year}"
            out.append(
                f'<text x="{LEFT + i * slot:.1f}" y="{TOP + plot_h + 20}" font-family="{SANS}" '
                f'font-size="11" fill="{MUTED}">{escape(label)}</text>'
            )
    if partial:
        out.append(
            f'<text x="{WIDTH - RIGHT}" y="{HEIGHT - 10}" text-anchor="end" font-family="{SANS}" '
            f'font-size="11" fill="{MUTED}">'
            f'<tspan fill="{PARTIAL}">■</tspan> {escape(text["partial"])}</text>'
        )
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    out_dir = Path(argv[1]) if len(argv) > 1 else Path("stats")
    try:
        weeks = weekly(fetch())
    except (OSError, ValueError, KeyError) as error:
        print(f"pypistats fetch failed: {error}", file=sys.stderr)
        return 1
    if not weeks:
        print("pypistats returned no data", file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    today = date.today()
    for lang in TEXT:
        (out_dir / f"downloads.{lang}.svg").write_text(render(weeks, lang, today), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
