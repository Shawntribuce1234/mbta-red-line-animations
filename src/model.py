"""
Takes the cleaned DataFrame from acquire.py and wraps it in a Pydantic model.
All the aggregation logic lives here so the animation files don't have to touch the raw data.
"""

import pandas as pd
from pydantic import BaseModel, computed_field


class SubwayLine(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    route_name: str
    route_id: str
    df: pd.DataFrame
    stop_order: list[str]

    @computed_field
    @property
    def stops(self) -> list[str]:
        # only keep stops that actually showed up in the data, in the right geographic order
        present = set(self.df["parent_station"].unique())
        return [s for s in self.stop_order if s in present]

    @computed_field
    @property
    def dates(self) -> list[str]:
        # grab all the unique dates and sort them so February goes in order
        return sorted(self.df["service_date"].astype(str).unique().tolist())

    @computed_field
    @property
    def daily_avg_travel(self) -> dict[str, float]:
        # add up all the stop segments per trip to get the full trip time, then average by day
        trip_totals = self.df.groupby(["service_date", "trip_id"])["travel_time_seconds"].sum()
        return {str(k): v for k, v in trip_totals.groupby("service_date").mean().items()}

    @computed_field
    @property
    def daily_avg_scheduled(self) -> dict[str, float]:
        # same thing but for scheduled times, dropping trips that never got matched to a schedule
        df_sched = self.df.dropna(subset=["scheduled_travel_time"])
        trip_totals = df_sched.groupby(["service_date", "trip_id"])["scheduled_travel_time"].sum()
        return {str(k): v for k, v in trip_totals.groupby("service_date").mean().items()}

    @computed_field
    @property
    def travel_by_stop_and_day(self) -> pd.DataFrame:
        # build a grid where each row is a stop, each column is a day, and the value is mean travel time
        pivot = self.df.pivot_table(
            index="parent_station",
            columns="service_date",
            values="travel_time_seconds",
            aggfunc="mean"
        )
        # reorder the rows so stops go north to south instead of alphabetical
        pivot = pivot.reindex([s for s in self.stop_order if s in pivot.index])
        return pivot