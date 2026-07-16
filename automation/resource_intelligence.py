"""
AI Resource Intelligence System — a small scheduled job that checks a list of
candidate source URLs and writes a reachability/freshness catalog for course
maintainers to review before linking any of them from a lesson.

This is a starting scaffold, not a production crawler: it only checks whether
a source is reachable, does not scrape or store third-party content, and every
result should still be reviewed by a human for quality, accuracy, and
copyright before it's used in a course.

Usage (one-off):
    pip install -r requirements.txt
    python resource_intelligence.py

Usage (recurring, every 6 hours):
    python resource_intelligence.py --schedule
"""
import argparse
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests
import schedule

SOURCES = [
    {"url": "https://hbr.org", "category": "Business & Entrepreneurship"},
    {"url": "https://www.investopedia.com", "category": "Finance & Accounting"},
    {"url": "https://blog.hubspot.com/marketing", "category": "Marketing & Sales"},
    {"url": "https://www.coursera.org", "category": "General reference"},
]


@dataclass
class ResourceCheck:
    url: str
    category: str
    reachable: bool
    checked_at: str


def check_source(source: dict, timeout: int = 8) -> ResourceCheck:
    try:
        response = requests.head(source["url"], timeout=timeout, allow_redirects=True)
        reachable = response.status_code < 400
    except requests.RequestException:
        reachable = False
    return ResourceCheck(
        url=source["url"],
        category=source["category"],
        reachable=reachable,
        checked_at=datetime.now(timezone.utc).isoformat(),
    )


def run_check(out_path: str = "resource_catalog.json") -> None:
    results = [check_source(s) for s in SOURCES]
    Path(out_path).write_text(json.dumps([asdict(r) for r in results], indent=2))
    reachable_count = sum(r.reachable for r in results)
    print(f"Checked {len(results)} sources ({reachable_count} reachable) -> {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Check and catalog learning resource sources.")
    parser.add_argument("--schedule", action="store_true", help="Run every 6 hours instead of once")
    args = parser.parse_args()

    if args.schedule:
        schedule.every(6).hours.do(run_check)
        run_check()
        print("Scheduled — checking every 6 hours. Ctrl+C to stop.")
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        run_check()


if __name__ == "__main__":
    main()
