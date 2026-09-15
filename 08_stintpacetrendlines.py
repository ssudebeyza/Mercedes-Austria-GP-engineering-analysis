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
# 3. Drivers
# -----------------------------------
drivers = ["RUS", "ANT"]

plt.figure(figsize=(12, 7))

# -----------------------------------
# 4. Process each driver
# -----------------------------------
for driver in drivers:

    laps = session.laps.pick_drivers(
        driver
    ).copy()

    # Remove invalid lap times
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

    # -----------------------------------
    # 5. Representative-lap filter
    # -----------------------------------
    median_time = (
        laps["LapTimeSeconds"]
        .median()
    )

    laps = laps[
        laps["LapTimeSeconds"]
        <= median_time * 1.055
    ].copy()

    # -----------------------------------
    # 6. Analyse each stint
    # -----------------------------------
    for stint_number, stint_laps in laps.groupby("Stint"):

        stint_laps = stint_laps.sort_values(
            "LapNumber"
        )

        # Need at least 3 points
        if len(stint_laps) < 3:
            continue

        # Lap numbers
        x = stint_laps[
            "LapNumber"
        ].to_numpy(dtype=float)

        # Lap times
        y = stint_laps[
            "LapTimeSeconds"
        ].to_numpy(dtype=float)

        # -----------------------------------
        # 7. Linear regression
        # -----------------------------------
        slope, intercept = np.polyfit(
            x,
            y,
            1
        )

        trend_line = (
            slope * x
            + intercept
        )

        # -----------------------------------
        # 8. Find compound
        # -----------------------------------
        compounds = (
            stint_laps["Compound"]
            .dropna()
        )

        if compounds.empty:
            compound = "UNKNOWN"
        else:
            compound = compounds.iloc[0]

        # -----------------------------------
        # 9. Print slope
        # -----------------------------------
        print(
            f"{driver} | "
            f"Stint {int(stint_number)} | "
            f"{compound} | "
            f"Slope = {slope:+.3f} s/lap"
        )

        # -----------------------------------
        # 10. Plot raw laps
        # -----------------------------------
        plt.scatter(
            x,
            y,
            s=20,
            alpha=0.35
        )

        # -----------------------------------
        # 11. Plot trendline
        # -----------------------------------
        plt.plot(
            x,
            trend_line,
            linewidth=2,
            label=(
                f"{driver} - "
                f"S{int(stint_number)} "
                f"{compound} "
                f"({slope:+.3f} s/lap)"
            )
        )

# -----------------------------------
# 12. Formatting
# -----------------------------------
plt.xlabel(
    "Lap Number"
)

plt.ylabel(
    "Representative Lap Time (s)"
)

plt.title(
    "2026 Austrian GP - Stint Pace Trendlines"
)

plt.legend(
    fontsize=8
)

plt.grid(
    alpha=0.3
)

plt.tight_layout()

# -----------------------------------
# 13. Save
# -----------------------------------
plt.savefig(
    "2026_austrian_gp_stint_pace_trendlines.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()