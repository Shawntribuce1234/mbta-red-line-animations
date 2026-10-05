# MBTA Red Line Travel-Time Animations

A Python visualization project exploring February 2026 MBTA Red Line performance data through two animations: a daily actual-versus-scheduled travel-time comparison and a station-by-day heatmap.

Completed for **DS3500** by **Shawn Tribuce**, the project separates data acquisition and cleaning, computed summaries, and animation into distinct modules. It includes a cached Parquet dataset and both exported MP4s.

## Repository Structure

```text
mbta-red-line-animations/
├── README.md
├── src/
│   ├── acquire.py
│   ├── model.py
│   ├── animate_a.py
│   └── animate_b.py
├── data/
│   └── february_data.parquet
├── demo/
│   ├── mbta_red_animation_a.mp4
│   └── mbta_red_animation_b.mp4
└── docs/
    └── reflection.md
```

Source filenames and contents are preserved. The original reflection is retained as coursework context. Submission metadata, personal contact details from that metadata, and Python cache files are excluded.

## Included Animations

- [Animation A: Actual versus scheduled travel time](demo/mbta_red_animation_a.mp4)
- [Animation B: Station-by-day heatmap](demo/mbta_red_animation_b.mp4)

These supplied MP4s can be viewed without installing Python or downloading data.

### Animation A

The line chart progressively reveals daily averages. Actual values are computed by summing retained `travel_time_seconds` within each service-date/trip pair, then averaging those trip sums by service date. Scheduled values follow the same aggregation after excluding records with missing `scheduled_travel_time`.

The animation uses a red actual line, a blue dashed scheduled line, and a shaded region labeled “Blizzard (Feb 20–23)” in the original code. That annotation is part of the author's presentation, not an independently verified weather classification.

### Animation B

The heatmap displays mean `travel_time_seconds` for each `parent_station` and service date. It reveals one date column per frame, using a fixed color scale calculated from the complete grid.

Rows use the project's hard-coded station-ID order. The plot includes 22 stations across the Red Line's branches; the row sequence should not be interpreted as a single continuous train journey. Missing grid cells remain missing.

Both scripts use Matplotlib `FuncAnimation`, a 200-millisecond display interval, and an FFmpeg export at five frames per second. They save an MP4 and then open a plot window.

## Data and Acquisition

`acquire.py` constructs daily Parquet URLs under the MBTA performance-data endpoint:

```text
https://performancedata.mbta.com/lamp/subway-on-time-performance-v1
```

It requests February 1–28, 2026, filters each successful daily response to `trunk_route_id == "Red"`, concatenates the results, and saves `february_data.parquet` in the current working directory.

If that cache exists and `force_refresh` is false, the function reads it directly. Daily download failures are printed and skipped; the code does not require all 28 downloads to succeed. It also does not distinguish cache files by route, so an existing cache is returned regardless of a newly requested route ID.

The included cache contains:

| Property | Verified value |
|---|---:|
| Raw rows | 180,114 |
| Columns | 27 |
| Rows after the supplied cleaner | 80,848 |
| Retained service dates | 28 |
| Retained parent stations | 22 |
| Retained rows missing scheduled travel time | 6,261 |
| Station-by-day grid | 22 × 28 |
| Missing cells in the grid | 10 |

The cache contains Red Line records only. Service dates are stored as values such as `20260201`; the model converts them to strings for its daily dictionaries and animation labels.

## Layered Implementation

### Acquisition and cleaning — `acquire.py`

The cleaner:

1. Sorts records by `stop_timestamp`.
2. Keeps the first record for each `trip_id` and `stop_id` pair.
3. Drops rows missing `travel_time_seconds`, `parent_station`, or `service_date`.

It does **not** drop records just because their scheduled travel time is missing. Those records are excluded only from the scheduled summary in the model.

### Computed summaries — `model.py`

The Pydantic `SubwayLine` model holds route metadata, the DataFrame, and station order. Computed properties provide:

- Stations present in the data, restricted to the configured station list.
- Sorted service-date strings.
- Daily mean actual trip sums.
- Daily mean scheduled trip sums.
- A pivot table of mean travel time by station and day.

The model allows an arbitrary Pandas DataFrame; it does not enforce a detailed row-level schema or validate trip completeness.

### Presentation — `animate_a.py` and `animate_b.py`

Both scripts load the data through the acquisition layer and use computed fields from `SubwayLine`. Frame updates reuse the existing line or image artists rather than creating new artists for every day.

## Observations from the Supplied Calculations

Running the original cleaner and aggregation logic on the included cache gives these selected daily actual averages:

| Service date | Mean sum of retained actual travel times, seconds |
|---|---:|
| February 20 | 1,555.1 |
| February 21 | 949.6 |
| February 22 | 942.4 |
| February 23 | 1,923.8 |

These values describe the current processing pipeline. They are not independently validated end-to-end journey durations, and their changes do not by themselves demonstrate a weather effect or a change in passenger demand.

The highest mean station-day travel time in the computed grid occurs at `place-brntn` on February 23, approximately **1,980.1 seconds**. The heatmap measures travel time, not ridership. Bright or blank cells cannot establish how many passengers traveled.

## Interpretation and Known Limitations

**Deduplication spans the whole month.** The cleaner uses `(trip_id, stop_id)` without `service_date`. In the raw cache, 1,629 trip IDs occur on more than one service date. Keeping only the earliest trip-stop record across the month can discard later-day observations and alter daily totals. This is a substantive limitation of the current outputs.

**Actual and scheduled averages need not use the same observations.** Actual summaries retain rows without schedules, while scheduled summaries exclude them. Partially matched trips can contribute partial scheduled sums. Differences between the lines therefore should not automatically be interpreted as delay estimates.

**Trip sums are not checked for completeness.** Branches, directions, and retained stop counts are pooled. The code does not require that a trip cover a complete route before adding it to the daily mean.

**Missing data can affect the display.** Animation A substitutes zero if an entire date has no scheduled summary. The supplied scheduled aggregation covers all 28 dates, but that fallback could be misleading with another cache. The shaded interval uses fixed frame positions and assumes all February dates are present.

**The reflection includes interpretations beyond the measured variables.** Its discussion of storms and passenger activity should be read as the author's hypotheses. Its statement that cleaning drops missing scheduled times differs from the implementation described above.

These limitations are documented without changing the submitted code or the supplied videos. The project demonstrates data organization, aggregation, and animation rather than a validated causal study of transit disruption.

## Running the Project

### Requirements

- Python 3.10 or later.
- Pandas, PyArrow, NumPy, Matplotlib, and Pydantic 2.
- Tk support and a graphical display: both scripts explicitly select Matplotlib's `TkAgg` backend.
- FFmpeg available to Matplotlib for MP4 export.

Install the Python packages:

```bash
python3 -m pip install pandas pyarrow numpy matplotlib "pydantic>=2,<3"
```

Tk and the FFmpeg executable are separate system requirements; the Python package command does not install them.

### Use the included cache

From the repository root:

```bash
cd data
python3 ../src/acquire.py
python3 ../src/animate_a.py
python3 ../src/animate_b.py
```

Run from `data/` because the unchanged scripts resolve the cache and video filenames relative to the current working directory. With the included cache present, `acquire.py` loads and cleans it, then prints the table shape and station IDs.

Newly rendered videos are written into `data/` as `mbta_red_animation_a.mp4` and `mbta_red_animation_b.mp4`. The supplied exports remain in `demo/`. Re-running an animation overwrites its same-named output in the working directory.

Each animation saves before opening its plot window; close the window when finished. If the cache is absent, the loading function attempts the remote download. A forced refresh is available through the Python function parameter `force_refresh=True`, not through a command-line flag.

## Verification

During repository preparation, the supplied Parquet file was read, the original cleaning function was executed, and the `SubwayLine` model was instantiated successfully. Its dates, stations, and heatmap dimensions were checked, and the daily and station-level aggregates were inspected. All four Python files passed syntax parsing.

No automated test suite is included. Remote downloads and MP4 rendering were not rerun during this review. The MP4s are preserved exports supplied with the assignment, not newly generated results.

## Author and Coursework

**Shawn Tribuce**  
**DS3500**

The original [reflection](docs/reflection.md) includes the author's discussion of the layered architecture, data limitations, and AI assistance used during development.
