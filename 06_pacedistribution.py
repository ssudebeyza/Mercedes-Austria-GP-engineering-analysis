import fastf1
import matplotlib.pyplot as plt

# -----------------------------------
# 1. Enable FastF1 cache
# -----------------------------------
fastf1.Cache.enable_cache("cache")

# -----------------------------------
# 2. Load 2026 Austrian GP race
# -----------------------------------
session = fastf1.get_session(2026, "Austria", "R")
session.load()

# -----------------------------------
# 3. Drivers
# -----------------------------------
drivers = ["RUS", "ANT"]

pace_data = []

# -----------------------------------
# 4. Prepare representative laps
# -----------------------------------
for driver in drivers:

    laps = session.laps.pick_drivers(driver).copy()

    # Remove laps without valid lap times
    laps = laps[laps["LapTime"].notna()]

    # Remove pit-in and pit-out laps
    laps = laps[
        laps["PitInTime"].isna()
        & laps["PitOutTime"].isna()
    ]

    # Convert lap time to seconds
    laps["LapTimeSeconds"] = (
        laps["LapTime"].dt.total_seconds()
    )

    # -----------------------------------
    # Representative-lap filter
    # -----------------------------------
    median_time = laps["LapTimeSeconds"].median()

    representative_laps = laps[
        laps["LapTimeSeconds"]
        <= median_time * 1.055
    ].copy()

    # Save data for plot
    pace_data.append(
        representative_laps["LapTimeSeconds"]
    )

    # -----------------------------------
    # Statistics
    # -----------------------------------
    mean_time = (
        representative_laps["LapTimeSeconds"].mean()
    )

    median_time = (
        representative_laps["LapTimeSeconds"].median()
    )

    std_time = (
        representative_laps["LapTimeSeconds"].std()
    )

    lap_count = len(representative_laps)

    print(f"\n{driver}")
    print("-----------------------------")
    print(f"Representative laps: {lap_count}")
    print(f"Mean:   {mean_time:.3f} s")
    print(f"Median: {median_time:.3f} s")
    print(f"Std:    {std_time:.3f} s")

# -----------------------------------
# 5. Create distribution plot
# -----------------------------------
plt.figure(figsize=(8, 6))

plt.boxplot(
    pace_data,
    tick_labels=drivers,
    showmeans=True
)

# -----------------------------------
# 6. Formatting
# -----------------------------------
plt.xlabel("Driver")
plt.ylabel("Representative Lap Time (s)")

plt.title(
    "2026 Austrian GP - Pace Distribution"
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

# -----------------------------------
# 7. Save figure
# -----------------------------------
plt.savefig(
    "2026_austrian_gp_pace_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()