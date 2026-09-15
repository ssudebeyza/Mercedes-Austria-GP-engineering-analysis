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
# 4. Calculate moving average
# -----------------------------------
for driver in drivers:

    laps = session.laps.pick_drivers(driver).copy()

    # Remove invalid lap times
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

    # Representative-lap filter
    median_time = laps["LapTimeSeconds"].median()

    laps = laps[
        laps["LapTimeSeconds"]
        <= median_time * 1.055
    ]

    # Sort laps
    laps = laps.sort_values("LapNumber")

    # Five-lap moving average
    laps["MovingAverage5"] = (
        laps["LapTimeSeconds"]
        .rolling(
            window=5,
            center=True,
            min_periods=2
        )
        .mean()
    )

    # Plot
    plt.plot(
        laps["LapNumber"],
        laps["MovingAverage5"],
        linewidth=2,
        label=driver
    )

# -----------------------------------
# 5. Formatting
# -----------------------------------
plt.xlabel("Lap Number")
plt.ylabel("5-Lap Moving Average (s)")

plt.title(
    "2026 Austrian GP - Five-Lap Moving Average"
)

plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()

# -----------------------------------
# 6. Save
# -----------------------------------
plt.savefig(
    "2026_austrian_gp_five_lap_moving_average.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()