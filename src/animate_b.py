
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from acquire import load, get_stop_order
from model import SubwayLine

"""
Animation B 
Shows a heatmap of mean travel time by stop and day building column by column.
Each column is one day, each row is a stop, color encodes how slow or fast travel was.
"""

def update(frame, im, data):
    # reveal one more column (day) of the heatmap each frame
    visible = data.copy()
    visible[:, frame + 1:] = np.nan
    im.set_array(visible)
    return [im]


def main():
    # load and clean the data from acquire.py
    df = load()

    # wrap the dataframe in the SubwayLine model to get computed fields
    line = SubwayLine(
        route_name="Red Line",
        route_id="Red",
        df=df,
        stop_order=get_stop_order()
    )

    # pull the pivot table out of the model — rows are stops, columns are days
    pivot = line.travel_by_stop_and_day

    # convert to a numpy array so we can mask columns with nan
    data = pivot.values.astype(float)

    # set vmin and vmax from the full dataset before animation starts
    # this keeps the colormap scale consistent across every frame
    vmin = np.nanmin(data)
    vmax = np.nanmax(data)

    # start with everything hidden — we'll reveal one column per frame
    initial = np.full_like(data, np.nan)

    fig, ax = plt.subplots(figsize=(14, 8))

    # create the heatmap artist once before the animation starts
    im = ax.imshow(
        initial,
        aspect="auto",
        cmap="plasma",
        vmin=vmin,
        vmax=vmax,
        interpolation="nearest"
    )

    # label the y axis with stop names in geographic order
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=8)

    # label the x axis with just the day number
    dates = line.dates
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels([d[6:] for d in dates], rotation=45, fontsize=8)

    ax.set_xlabel("Day of February 2026")
    ax.set_title("Red Line — Mean Travel Time by Stop and Day, February 2026")

    # add a colorbar so we know what the colors mean
    plt.colorbar(im, ax=ax, label="Mean Travel Time (seconds)")

    # build the animation — one frame per day, fargs passes the data and image artist
    anim = FuncAnimation(
        fig,
        update,
        frames=len(dates),
        fargs=(im, data),
        interval=200,
        blit=True,
        repeat=False
    )

    # save as mp4 then show the window
    anim.save("mbta_red_animation_b.mp4", writer="ffmpeg", fps=5)
    plt.show()


if __name__ == "__main__":
    main()