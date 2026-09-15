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

sector_results = {}

# -----------------------------------
# 4. Process each driver
# -----------------------------------
for driver in drivers:

    laps = session.laps.pick_drivers(
        driver
    ).copy()

    # Remove laps without valid lap time
    laps = laps[
        laps["LapTime"].notna()
    ]

    # Remove pit-in and pit-out laps
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
    median_lap_time = (
        laps["LapTimeSeconds"]
        .median()
    )

    laps = laps[
        laps["LapTimeSeconds"]
        <= median_lap_time * 1.055
    ].copy()

    # -----------------------------------
    # 6. Sector times to seconds
    # -----------------------------------
    laps["Sector1Seconds"] = (
        laps["Sector1Time"]
        .dt
        .total_seconds()
    )

    laps["Sector2Seconds"] = (
        laps["Sector2Time"]
        .dt
        .total_seconds()
    )

    laps["Sector3Seconds"] = (
        laps["Sector3Time"]
        .dt
        .total_seconds()
    )

    # -----------------------------------
    # 7. Calculate median sector times
    # -----------------------------------
    sector1 = laps[
        "Sector1Seconds"
    ].median()

    sector2 = laps[
        "Sector2Seconds"
    ].median()

    sector3 = laps[
        "Sector3Seconds"
    ].median()

    sector_results[driver] = [
        sector1,
        sector2,
        sector3
    ]

    # -----------------------------------
    # 8. Print results
    # -----------------------------------
    print(f"\n{driver}")
    print("----------------------")
    print(f"Sector 1: {sector1:.4f} s")
    print(f"Sector 2: {sector2:.4f} s")
    print(f"Sector 3: {sector3:.4f} s")

# -----------------------------------
# 9. Calculate sector deltas
# -----------------------------------
print("\nSECTOR DELTA: ANT - RUS")
print("----------------------")

for i in range(3):

    delta = (
        sector_results["ANT"][i]
        - sector_results["RUS"][i]
    )

    print(
        f"Sector {i + 1}: "
        f"{delta:+.4f} s"
    )

# -----------------------------------
# 10. Prepare plot
# -----------------------------------
sectors = [
    "Sector 1",
    "Sector 2",
    "Sector 3"
]

x = np.arange(
    len(sectors)
)

width = 0.35

fig, ax = plt.subplots(
    figsize=(9, 6)
)

# -----------------------------------
# 11. Russell bars
# -----------------------------------
ax.bar(
    x - width / 2,
    sector_results["RUS"],
    width,
    label="RUS"
)

# -----------------------------------
# 12. Antonelli bars
# -----------------------------------
ax.bar(
    x + width / 2,
    sector_results["ANT"],
    width,
    label="ANT"
)

# -----------------------------------
# 13. Formatting
# -----------------------------------
ax.set_xlabel(
    "Sector"
)

ax.set_ylabel(
    "Median Sector Time (s)"
)

ax.set_title(
    "2026 Austrian GP - Sector Pace Comparison"
)

ax.set_xticks(
    x
)

ax.set_xticklabels(
    sectors
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
    "2026_austrian_gp_sector_pace_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()