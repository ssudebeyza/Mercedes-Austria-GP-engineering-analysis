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
# 3. Selected representative targets
# -----------------------------------
target_times = {
    "RUS": 70.683,
    "ANT": 70.374
}

telemetry_data = {}

# -----------------------------------
# 4. Find selected representative lap
# -----------------------------------
for driver in ["RUS", "ANT"]:

    laps = session.laps.pick_drivers(
        driver
    ).copy()

    # Valid laps only
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

    # -----------------------------------
    # 5. Get telemetry
    # -----------------------------------
    telemetry = (
        selected_lap
        .get_telemetry()
        .add_distance()
    )

    telemetry = telemetry[
        ["Distance", "Time", "Speed"]
    ].dropna().copy()

    # Time elapsed from start of telemetry
    telemetry["ElapsedTime"] = (
        telemetry["Time"]
        - telemetry["Time"].iloc[0]
    ).dt.total_seconds()

    # Remove duplicate distance samples
    telemetry = telemetry.drop_duplicates(
        subset="Distance"
    )

    telemetry = telemetry.sort_values(
        "Distance"
    )

    telemetry_data[driver] = telemetry

# -----------------------------------
# 6. Determine common distance range
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

# Common distance grid
distance_grid = np.linspace(
    start_distance,
    end_distance,
    5000
)

# -----------------------------------
# 7. Interpolate elapsed time
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
# 8. Calculate cumulative delta
# -----------------------------------
# Delta = ANT - RUS
#
# Negative = Antonelli ahead in elapsed time
# Positive = Russell ahead in elapsed time

delta = (
    ant_elapsed
    - rus_elapsed
)

# -----------------------------------
# 9. Print final delta
# -----------------------------------
print("\nCUMULATIVE LAP DELTA")
print("-----------------------------")

print(
    f"Final telemetry delta: "
    f"{delta[-1]:+.3f} s"
)

print(
    "Negative = ANT advantage"
)

print(
    "Positive = RUS advantage"
)

# -----------------------------------
# 10. Plot cumulative delta
# -----------------------------------
plt.figure(
    figsize=(12, 6)
)

plt.plot(
    distance_grid,
    delta,
    linewidth=2
)

# Zero reference line
plt.axhline(
    0,
    linewidth=1,
    linestyle="--"
)

# -----------------------------------
# 11. Formatting
# -----------------------------------
plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Cumulative Time Delta (s)"
)

plt.title(
    "2026 Austrian GP - Cumulative Representative Lap Delta"
)

plt.grid(
    alpha=0.3
)

plt.tight_layout()

# -----------------------------------
# 12. Save
# -----------------------------------
plt.savefig(
    "2026_austrian_gp_cumulative_lap_delta.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()