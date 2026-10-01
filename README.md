# san-antonio-weather

A daily weather dataset for San Antonio, Texas, collected automatically.

A scheduled GitHub Actions workflow runs every morning, fetches the previous
day's summary from the [Open-Meteo](https://open-meteo.com/) API, and commits
it to [`data/daily.csv`](data/daily.csv). Commits with the message
`data: daily snapshot ... (automated)` are made by that workflow, not by hand.

## Data

One row per calendar day (America/Chicago time) at 29.4241, -98.4936.

| Column | Meaning |
|---|---|
| `date` | Local date, `YYYY-MM-DD` |
| `temp_max_f`, `temp_min_f`, `temp_mean_f` | Air temperature at 2 m, °F |
| `humidity_mean_pct` | Mean relative humidity at 2 m, % |
| `precipitation_in` | Total precipitation, inches |
| `wind_max_mph`, `wind_gust_max_mph` | Maximum wind speed and gust at 10 m, mph |
| `weather_code` | [WMO weather code](https://open-meteo.com/en/docs#weathervariables) for the day |

The values come from Open-Meteo's weather-model grid cell for the city, not
from a single weather station, so they can differ slightly from airport
observations.

## How it works

- [`collect.py`](collect.py) (Python standard library only) asks the API for
  the last 7 days and appends any dates missing from the CSV, so a skipped run
  is filled in by the next one.
- [`.github/workflows/collect.yml`](.github/workflows/collect.yml) runs it
  daily at 12:15 UTC and commits the result if there is a new row.

Run it locally:

```bash
python collect.py
```

## Attribution

Weather data by [Open-Meteo.com](https://open-meteo.com/), licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
