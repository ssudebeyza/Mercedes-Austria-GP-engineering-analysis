import fastf1
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------------
# 1. Enable FastF1 cache
# -----------------------------------
fastf1.Cache.enable_cache("cache")

# -----------------------------------
# 2. Load race
# -----------------------------------
session = fastf1.get_session(
    2026,
    "Austria",
    "R"
)

session.load()

# -----------------------------------
# 3. Selected representative laps
# -----------------------------------
target_times = {
    "RUS": 70.683,
    "ANT": 70.374
}

telemetry_data = {}

# -----------------------------------
# 4. Get selected-lap telemetry
# -----------------------------------
for driver in ["RUS", "ANT"]:

    laps = session.laps.pick_drivers(
        driver
    ).copy()

    laps = laps[
        laps["LapTime"].notna()
    ]

    laps = laps[
        laps["PitInTime"].isna()
        & laps["PitOutTime"].isna()
    ]

    laps["LapTimeSeconds"] = (
        laps["LapTime"]
        .dt
        .total_seconds()
    )

    # Find lap closest to report target
    target = target_times[driver]

    index = (
        laps["LapTimeSeconds"]
        - target
    ).abs().idxmin()

    selected_lap = laps.loc[index]

    print(
        f"{driver}: "
        f"Lap {int(selected_lap['LapNumber'])} - "
        f"{selected_lap['LapTimeSeconds']:.3f} s"
    )

    telemetry = (
        selected_lap
        .get_telemetry()
        .add_distance()
    )

    telemetry = telemetry[
        ["Distance", "Time"]
    ].dropna().copy()

    telemetry["ElapsedTime"] = (
        telemetry["Time"]
        - telemetry["Time"].iloc[0]
    ).dt.total_seconds()

    telemetry = telemetry.drop_duplicates(
        subset="Distance"
    )

    telemetry = telemetry.sort_values(
        "Distance"
    )

    telemetry_data[driver] = telemetry

# -----------------------------------
# 5. Common distance grid
# -----------------------------------
rus = telemetry_data["RUS"]
ant = telemetry_data["ANT"]

start_distance = max(
    rus["Distance"].min(),
    ant["Distance"].min()
)

end_distance = min(
    rus["Distance"].max(),
    ant["Distance"].max()
)

distance_grid = np.linspace(
    start_distance,
    end_distance,
    5000
)

# -----------------------------------
# 6. Interpolate elapsed time
# -----------------------------------
rus_elapsed = np.interp(
    distance_grid,
    rus["Distance"],
    rus["ElapsedTime"]
)

ant_elapsed = np.interp(
    distance_grid,
    ant["Distance"],
    ant["ElapsedTime"]
)

# Delta = ANT - RUS
cumulative_delta = (
    ant_elapsed
    - rus_elapsed
)

# -----------------------------------
# 7. Get circuit corner locations
# -----------------------------------
circuit_info = session.get_circuit_info()

corners = circuit_info.corners.copy()

# Keep selected corners used in report
selected_corner_numbers = [
    1,
    3,
    4,
    6,
    7,
    9,
    10
]

corner_results = {}

# -----------------------------------
# 8. Calculate delta for each corner
# -----------------------------------
for corner_number in selected_corner_numbers:

    corner_row = corners[
        corners["Number"] == corner_number
    ]

    if corner_row.empty:
        continue

    corner_center = float(
        corner_row["Distance"].iloc[0]
    )

    # Generic analysis window
    # around the official corner location
    window_start = corner_center - 150
    window_end = corner_center + 150

    # Delta at beginning of window
    delta_start = np.interp(
        window_start,
        distance_grid,
        cumulative_delta
    )

    # Delta at end of window
    delta_end = np.interp(
        window_end,
        distance_grid,
        cumulative_delta
    )

    # Change in cumulative delta
    corner_delta = (
        delta_end
        - delta_start
    )

    corner_results[
        f"T{corner_number}"
    ] = corner_delta

# -----------------------------------
# 9. Print corner deltas
# -----------------------------------
print("\nCORNER PERFORMANCE DELTA")
print("--------------------------------")

print(
    "Delta = ANT - RUS"
)

print(
    "Negative = ANT advantage"
)

print(
    "Positive = RUS advantage\n"
)

for corner, delta in corner_results.items():

    if delta < 0:
        advantage = "ANT"
    else:
        advantage = "RUS"

    print(
        f"{corner}: "
        f"{delta:+.3f} s "
        f"({advantage} advantage)"
    )

# -----------------------------------
# 10. Prepare plot
# -----------------------------------
corner_names = list(
    corner_results.keys()
)

corner_deltas = list(
    corner_results.values()
)

plt.figure(
    figsize=(10, 6)
)

bars = plt.bar(
    corner_names,
    corner_deltas
)

# -----------------------------------
# 11. Add delta labels
# -----------------------------------
for bar, delta in zip(
    bars,
    corner_deltas
):

    if delta >= 0:
        vertical_alignment = "bottom"
        y_position = delta + 0.003

    else:
        vertical_alignment = "top"
        y_position = delta - 0.003

    plt.text(
        bar.get_x()
        + bar.get_width() / 2,

        y_position,

        f"{delta:+.3f}",

        ha="center",
        va=vertical_alignment,
        fontsize=9
    )

# -----------------------------------
# 12. Zero reference
# -----------------------------------
plt.axhline(
    0,
    linewidth=1,
    linestyle="--"
)

# -----------------------------------
# 13. Formatting
# -----------------------------------
plt.xlabel(
    "Corner"
)

plt.ylabel(
    "Selected-Corner Delta (s)"
)

plt.title(
    "2026 Austrian GP - Corner Performance Delta"
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

# -----------------------------------
# 14. Save
# -----------------------------------
plt.savefig(
    "2026_austrian_gp_corner_performance_delta.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()