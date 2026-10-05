
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from acquire import load, get_stop_order
from model import SubwayLine


"""
Animation A
Shows actual vs scheduled mean travel time building day by day across February.
You can clearly see the blizzard impact around Feb 20-23.
"""


def update(frame, line, dates, actual_vals, sched_vals, actual_line, sched_line):
    # build the x axis as a list of indices up to the current frame
    x = list(range(frame + 1))
    # add one more day of actual travel time to the red line
    actual_line.set_data(x, actual_vals[:frame + 1])
    # add one more day of scheduled travel time to the blue dashed line
    sched_line.set_data(x, sched_vals[:frame + 1])
    return actual_line, sched_line


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

    # pull the dates and values out of the model for use in the animation
    dates = line.dates
    actual_vals = [line.daily_avg_travel[d] for d in dates]
    sched_vals = [line.daily_avg_scheduled.get(d, 0) for d in dates]

    # set up the figure and axis
    fig, ax = plt.subplots(figsize=(12, 5))

    # x axis spans all 28 days, y axis gives a little headroom above the max value
    ax.set_xlim(0, len(dates) - 1)
    ax.set_ylim(0, max(actual_vals + sched_vals) * 1.1)

    # label the x axis with just the day number instead of the full date string
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels([d[6:] for d in dates], rotation=45)
    ax.set_xlabel("Day of February 2026")
    ax.set_ylabel("Mean Travel Time (seconds)")
    ax.set_title("Red Line — Actual vs Scheduled Travel Time, February 2026")

    # shade the blizzard window so its easy to see on the chart
    ax.axvspan(19, 22, alpha=0.15, color="blue", label="Blizzard (Feb 20–23)")

    # create both line artists once before the animation starts — never create inside update
    actual_line, = ax.plot([], [], color="tomato", label="Actual")
    sched_line, = ax.plot([], [], color="steelblue", linestyle="--", label="Scheduled")
    ax.legend()

    # build the animation — one frame per day, fargs passes everything update needs
    anim = FuncAnimation(
        fig,
        update,
        frames=len(dates),
        fargs=(line, dates, actual_vals, sched_vals, actual_line, sched_line),
        interval=200,
        blit=True,
        repeat=False
    )

    # save as mp4 then show the window
    anim.save("mbta_red_animation_a.mp4", writer="ffmpeg", fps=5)
    plt.show()


if __name__ == "__main__":
    main()