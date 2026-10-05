import pandas as pd
from datetime import date, timedelta
from pathlib import Path

"""
Data acquisition layer 

Fetches and cleans 28 days of February 2026 performance data
from the LAMP public API and returns a analysis-ready DataFrame.
"""

CACHE_PATH = Path("february_data.parquet")
BASE_URL = "https://performancedata.mbta.com/lamp/subway-on-time-performance-v1"

RED_LINE_STOP_ORDER = [
    "place-alfcl",
    "place-davis",
    "place-portr",
    "place-harsq",
    "place-cntsq",
    "place-knncl",
    "place-chmnl",
    "place-pktrm",
    "place-dwnxg",
    "place-sstat",
    "place-brdwy",
    "place-andrw",
    "place-jfk",
    "place-nqncy",
    "place-qnctr",
    "place-qamnl",
    "place-brntn",
    "place-shmnl",
    "place-fldcr",
    "place-smmnl",
    "place-wlsta",
    "place-asmnl",
]


def fetch_february(route_id: str = "Red", force_refresh: bool = False) -> pd.DataFrame:
    if CACHE_PATH.exists() and not force_refresh:
        return pd.read_parquet(CACHE_PATH)

    frames = []
    start = date(2026, 2, 1)

    for i in range(28):
        day = start + timedelta(days=i)
        url = f"{BASE_URL}/{day}-subway-on-time-performance-v1.parquet"
        try:
            df = pd.read_parquet(url)
            # Filter down to only Red Line rows
            df = df[df["trunk_route_id"] == route_id]
            frames.append(df)
        except Exception as e:
            print(f"Warning: could not fetch {day}: {e}")

    # Combine all 28 days into one table
    combined = pd.concat(frames, ignore_index=True)
    combined.to_parquet(CACHE_PATH)
    return combined


def clean(df: pd.DataFrame) -> pd.DataFrame:
    # Put the earliest record on top for each trip+stop
    df = df.sort_values("stop_timestamp")
    # used to remove duplicate trip+stop pairs
    df = df.drop_duplicates(subset=["trip_id", "stop_id"], keep="first")
    # Remove rows with missing travel time, station, or date
    df = df.dropna(subset=["travel_time_seconds", "parent_station", "service_date"])
    return df


def get_stop_order() -> list[str]:
    # Return stations in geographic order for the heatmap
    return RED_LINE_STOP_ORDER


def load(route_id: str = "Red", force_refresh: bool = False) -> pd.DataFrame:
    # Fetch and clean the data in one step
    raw = fetch_february(route_id=route_id, force_refresh=force_refresh)
    return clean(raw)


if __name__ == "__main__":
    df = load()
    print(df.shape)
    print(df["parent_station"].unique())