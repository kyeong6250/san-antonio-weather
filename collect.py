"""Append completed daily weather summaries for San Antonio, TX to data/daily.csv.

Fetches the last few days from the Open-Meteo API and adds any dates the CSV
does not have yet, so a missed run is filled in by the next one.
"""

import argparse
import csv
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

LATITUDE = 29.4241
LONGITUDE = -98.4936
TIMEZONE = "America/Chicago"
API_URL = "https://api.open-meteo.com/v1/forecast"
CSV_PATH = Path(__file__).parent / "data" / "daily.csv"

# CSV column -> Open-Meteo daily variable
FIELDS = {
    "temp_max_f": "temperature_2m_max",
    "temp_min_f": "temperature_2m_min",
    "temp_mean_f": "temperature_2m_mean",
    "humidity_mean_pct": "relative_humidity_2m_mean",
    "precipitation_in": "precipitation_sum",
    "wind_max_mph": "wind_speed_10m_max",
    "wind_gust_max_mph": "wind_gusts_10m_max",
    "weather_code": "weather_code",
}
HEADER = ["date", *FIELDS]


def fetch_daily(past_days):
    query = urllib.parse.urlencode(
        {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "daily": ",".join(FIELDS.values()),
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": TIMEZONE,
            "past_days": past_days,
            "forecast_days": 1,
        }
    )
    with urllib.request.urlopen(f"{API_URL}?{query}", timeout=30) as response:
        daily = json.load(response)["daily"]

    rows = [
        {"date": day, **{col: daily[var][i] for col, var in FIELDS.items()}}
        for i, day in enumerate(daily["time"])
    ]
    # The last entry is today in San Antonio, which is not over yet.
    return rows[:-1]


def read_existing():
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open(newline="") as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=7, help="how many past days to check (max 92)")
    args = parser.parse_args()

    existing = read_existing()
    known = {row["date"] for row in existing}
    new_rows = [
        row
        for row in fetch_daily(args.days)
        if row["date"] not in known and all(v is not None for v in row.values())
    ]
    if not new_rows:
        print("No new days to add.")
        return 0

    rows = sorted(existing + new_rows, key=lambda row: row["date"])
    CSV_PATH.parent.mkdir(exist_ok=True)
    with CSV_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Added {len(new_rows)} day(s): {new_rows[0]['date']} to {new_rows[-1]['date']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
