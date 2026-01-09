#!/usr/bin/env python3
"""
Generate PyPI download statistics chart for Aetheris.

This script fetches download data from pypistats.org and generates
an SVG chart showing download trends over time.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Package configuration
PACKAGE_NAME = "adryserage-aetheris"
OUTPUT_DIR = Path("assets/charts")
CHART_FILE = OUTPUT_DIR / "downloads.svg"
DATA_FILE = OUTPUT_DIR / "downloads.json"


def install_dependencies():
    """Install required packages if not present."""
    try:
        import matplotlib
        import pypistats
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypistats", "matplotlib"])


def fetch_download_data():
    """Fetch download statistics from pypistats.org."""
    import pypistats

    # Get overall downloads (last 180 days available)
    data = pypistats.overall(PACKAGE_NAME, total=False, format="json")
    return json.loads(data)


def generate_chart(data: dict):
    """Generate SVG chart from download data."""
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime

    # Parse data
    records = data.get("data", [])
    if not records:
        print("No download data available")
        return False

    # Filter for 'without_mirrors' category and sort by date
    filtered = [r for r in records if r.get("category") == "without_mirrors"]
    filtered.sort(key=lambda x: x["date"])

    if not filtered:
        print("No 'without_mirrors' data available")
        return False

    dates = [datetime.strptime(r["date"], "%Y-%m-%d") for r in filtered]
    downloads = [r["downloads"] for r in filtered]

    # Calculate cumulative downloads
    cumulative = []
    total = 0
    for d in downloads:
        total += d
        cumulative.append(total)

    # Create figure with dark theme
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), height_ratios=[1, 1])
    fig.patch.set_facecolor('#0d1117')

    # Daily downloads chart
    ax1.fill_between(dates, downloads, alpha=0.3, color='#58a6ff')
    ax1.plot(dates, downloads, color='#58a6ff', linewidth=1.5)
    ax1.set_ylabel('Daily Downloads', color='#8b949e')
    ax1.tick_params(colors='#8b949e')
    ax1.set_facecolor('#0d1117')
    ax1.spines['bottom'].set_color('#30363d')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color('#30363d')
    ax1.grid(True, alpha=0.2, color='#30363d')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))

    # Cumulative downloads chart
    ax2.fill_between(dates, cumulative, alpha=0.3, color='#3fb950')
    ax2.plot(dates, cumulative, color='#3fb950', linewidth=1.5)
    ax2.set_ylabel('Cumulative Downloads', color='#8b949e')
    ax2.set_xlabel('Date', color='#8b949e')
    ax2.tick_params(colors='#8b949e')
    ax2.set_facecolor('#0d1117')
    ax2.spines['bottom'].set_color('#30363d')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color('#30363d')
    ax2.grid(True, alpha=0.2, color='#30363d')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))

    # Title
    total_downloads = sum(downloads)
    fig.suptitle(
        f'Aetheris PyPI Downloads (Last 180 Days) - Total: {total_downloads:,}',
        color='#f0f6fc',
        fontsize=12,
        fontweight='bold'
    )

    plt.tight_layout()

    # Save chart
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(CHART_FILE, format='svg', facecolor='#0d1117', edgecolor='none', bbox_inches='tight')
    plt.close()

    print(f"Chart saved to {CHART_FILE}")
    return True


def save_stats(data: dict):
    """Save download statistics to JSON file."""
    records = data.get("data", [])
    filtered = [r for r in records if r.get("category") == "without_mirrors"]

    total = sum(r["downloads"] for r in filtered)

    stats = {
        "package": PACKAGE_NAME,
        "total_downloads_180d": total,
        "last_updated": datetime.now().isoformat(),
        "data_points": len(filtered)
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"Stats saved to {DATA_FILE}")
    return stats


def main():
    """Main entry point."""
    print(f"Fetching download stats for {PACKAGE_NAME}...")

    install_dependencies()

    try:
        data = fetch_download_data()
        generate_chart(data)
        stats = save_stats(data)

        print(f"\nTotal downloads (180 days): {stats['total_downloads_180d']:,}")
        print("Done!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
