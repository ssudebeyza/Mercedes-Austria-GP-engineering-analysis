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

plt.figure(figsize=(11, 6))

# -----------------------------------
# 4. Process each driver
# -----------------------------------
for driver in drivers:

    laps = session.laps.pick_drivers(driver).copy()

    # Remove laps without a valid lap time
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
    # Remove major outliers
    # -----------------------------------
    median_time = laps["LapTimeSeconds"].median()

    representative_laps = laps[
        laps["LapTimeSeconds"] <= median_time * 1.055
    ]

    # -----------------------------------
    # Plot
    # -----------------------------------
    plt.plot(
        representative_laps["LapNumber"],
        representative_laps["LapTimeSeconds"],
        marker="o",
        markersize=3,
        linewidth=1.2,
        label=driver
    )

# -----------------------------------
# 5. Formatting
# -----------------------------------
plt.xlabel("Lap Number")
plt.ylabel("Lap Time (s)")

plt.title(
    "2026 Austrian GP - Lap Time Evolution"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

# -----------------------------------
# 6. Save
# -----------------------------------
plt.savefig(
    "2026_austrian_gp_lap_time_evolution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()