import fastf1
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------------
# 1. Enable FastF1 cache
# -----------------------------------
fastf1.Cache.enable_cache("cache")

# -----------------------------------
# 2. Load 2026 Austrian GP race
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

    # Valid lap times only
    laps = laps[
        laps["LapTime"].notna()
    ]

    # Remove pit-in / pit-out laps
    laps = laps[
        laps["PitInTime"].isna()
        & laps["PitOutTime"].isna()
    ]

    # Convert lap time to seconds
    laps["LapTimeSeconds"] = (
        laps["LapTime"]
        .dt
        .total_seconds()
    )

    # Find lap closest to selected target
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

    # Get telemetry
    telemetry = (
        selected_lap
        .get_telemetry()
        .add_distance()
    )

    telemetry = telemetry[
        ["Distance", "Time"]
    ].dropna().copy()

    # Elapsed time
    telemetry["ElapsedTime"] = (
        telemetry["Time"]
        - telemetry["Time"].iloc[0]
    ).dt.total_seconds()

    # Clean distance data
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

# -----------------------------------
# 7. Cumulative delta
# -----------------------------------
# Delta = ANT - RUS
#
# Negative = ANT gains time
# Positive = RUS gains time

cumulative_delta = (
    ant_elapsed
    - rus_elapsed
)

# -----------------------------------
# 8. Get circuit corner positions
# -----------------------------------
circuit_info = session.get_circuit_info()

corners = circuit_info.corners.copy()

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
# 9. Calculate corner deltas
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

    # Generic screening window
    window_start = (
        corner_center - 150
    )

    window_end = (
        corner_center + 150
    )

    delta_start = np.interp(
        window_start,
        distance_grid,
        cumulative_delta
    )

    delta_end = np.interp(
        window_end,
        distance_grid,
        cumulative_delta
    )

    corner_delta = (
        delta_end
        - delta_start
    )

    corner_results[
        f"T{corner_number}"
    ] = corner_delta

# -----------------------------------
# 10. Convert delta into loss
# -----------------------------------
rus_losses = []
ant_losses = []

for delta in corner_results.values():

    if delta < 0:
        # ANT gained time
        # therefore RUS lost time
        rus_losses.append(
            abs(delta)
        )

        ant_losses.append(
            0
        )

    else:
        # RUS gained time
        # therefore ANT lost time
        rus_losses.append(
            0
        )

        ant_losses.append(
            abs(delta)
        )

# -----------------------------------
# 11. Print results
# -----------------------------------
print("\nCORNER LOSS MAP")
print("--------------------------------")

for corner, delta in corner_results.items():

    if delta < 0:

        print(
            f"{corner}: "
            f"RUS loss = {abs(delta):.3f} s"
        )

    else:

        print(
            f"{corner}: "
            f"ANT loss = {abs(delta):.3f} s"
        )

# -----------------------------------
# 12. Plot
# -----------------------------------
corner_names = list(
    corner_results.keys()
)

x = np.arange(
    len(corner_names)
)

width = 0.35

fig, ax = plt.subplots(
    figsize=(10, 6)
)

ax.bar(
    x - width / 2,
    rus_losses,
    width,
    label="RUS Loss"
)

ax.bar(
    x + width / 2,
    ant_losses,
    width,
    label="ANT Loss"
)

# -----------------------------------
# 13. Formatting
# -----------------------------------
ax.set_xlabel(
    "Corner"
)

ax.set_ylabel(
    "Relative Time Loss (s)"
)

ax.set_title(
    "2026 Austrian GP - Corner Performance Loss Map"
)

ax.set_xticks(
    x
)

ax.set_xticklabels(
    corner_names
)

ax.legend()

ax.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

# -----------------------------------
# 14. Save
# -----------------------------------
plt.savefig(
    "2026_austrian_gp_corner_performance_loss_map.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()