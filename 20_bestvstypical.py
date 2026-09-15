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
# 3. Selected strong representative laps
# -----------------------------------
selected_targets = {
    "RUS": 70.683,
    "ANT": 70.374
}

drivers = ["RUS", "ANT"]

results = {}

# -----------------------------------
# 4. Process each driver
# -----------------------------------
for driver in drivers:

    laps = session.laps.pick_drivers(
        driver
    ).copy()

    # Valid lap times
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
    median_all = (
        laps["LapTimeSeconds"]
        .median()
    )

    representative = laps[
        laps["LapTimeSeconds"]
        <= median_all * 1.055
    ].copy()

    # -----------------------------------
    # 6. Strong selected representative lap
    # -----------------------------------
    target = selected_targets[
        driver
    ]

    strong_index = (
        representative["LapTimeSeconds"]
        - target
    ).abs().idxmin()

    strong_lap = representative.loc[
        strong_index
    ]

    # -----------------------------------
    # 7. Typical representative lap
    # -----------------------------------
    representative_median = (
        representative[
            "LapTimeSeconds"
        ].median()
    )

    typical_index = (
        representative[
            "LapTimeSeconds"
        ]
        - representative_median
    ).abs().idxmin()

    typical_lap = representative.loc[
        typical_index
    ]

    # -----------------------------------
    # 8. Store results
    # -----------------------------------
    results[driver] = {
        "representative": representative,
        "strong": strong_lap,
        "typical": typical_lap,
        "median": representative_median
    }

    # -----------------------------------
    # 9. Print information
    # -----------------------------------
    print(f"\n{driver}")
    print("-----------------------------")

    print(
        f"Selected representative lap: "
        f"Lap {int(strong_lap['LapNumber'])} "
        f"({strong_lap['LapTimeSeconds']:.3f} s)"
    )

    print(
        f"Typical representative lap: "
        f"Lap {int(typical_lap['LapNumber'])} "
        f"({typical_lap['LapTimeSeconds']:.3f} s)"
    )

    print(
        f"Representative median: "
        f"{representative_median:.3f} s"
    )

    print(
        f"Selected-to-typical difference: "
        f"{strong_lap['LapTimeSeconds'] - typical_lap['LapTimeSeconds']:+.3f} s"
    )

# ===================================
# FIGURE 6.6
# LAP-TIME COMPARISON
# ===================================

labels = [
    "RUS Selected",
    "RUS Typical",
    "ANT Selected",
    "ANT Typical"
]

times = [
    results["RUS"]["strong"]["LapTimeSeconds"],
    results["RUS"]["typical"]["LapTimeSeconds"],
    results["ANT"]["strong"]["LapTimeSeconds"],
    results["ANT"]["typical"]["LapTimeSeconds"]
]

plt.figure(
    figsize=(9, 6)
)

bars = plt.bar(
    labels,
    times
)

# Add values
for bar, time in zip(
    bars,
    times
):

    plt.text(
        bar.get_x()
        + bar.get_width() / 2,
        time + 0.02,
        f"{time:.3f}",
        ha="center",
        va="bottom"
    )

plt.ylabel(
    "Lap Time (s)"
)

plt.title(
    "2026 Austrian GP - Selected vs Typical Representative Lap"
)

plt.xticks(
    rotation=20
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_selected_vs_typical_laptime.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ===================================
# 10. Telemetry function
# ===================================

def get_telemetry(lap):

    telemetry = (
        lap
        .get_telemetry()
        .add_distance()
    )

    telemetry = telemetry[
        [
            "Distance",
            "Speed",
            "Throttle",
            "Brake"
        ]
    ].dropna().copy()

    telemetry = telemetry.drop_duplicates(
        subset="Distance"
    )

    telemetry = telemetry.sort_values(
        "Distance"
    )

    return telemetry

# -----------------------------------
# 11. Get telemetry
# -----------------------------------
telemetry = {}

for driver in drivers:

    telemetry[
        f"{driver}_selected"
    ] = get_telemetry(
        results[driver]["strong"]
    )

    telemetry[
        f"{driver}_typical"
    ] = get_telemetry(
        results[driver]["typical"]
    )

# ===================================
# FIGURE 6.7
# SPEED PROFILE COMPARISON
# ===================================

plt.figure(
    figsize=(12, 6)
)

# Russell selected
plt.plot(
    telemetry["RUS_selected"]["Distance"],
    telemetry["RUS_selected"]["Speed"],
    linewidth=1.8,
    label="RUS - Selected"
)

# Russell typical
plt.plot(
    telemetry["RUS_typical"]["Distance"],
    telemetry["RUS_typical"]["Speed"],
    linewidth=1.3,
    linestyle="--",
    label="RUS - Typical"
)

# Antonelli selected
plt.plot(
    telemetry["ANT_selected"]["Distance"],
    telemetry["ANT_selected"]["Speed"],
    linewidth=1.8,
    label="ANT - Selected"
)

# Antonelli typical
plt.plot(
    telemetry["ANT_typical"]["Distance"],
    telemetry["ANT_typical"]["Speed"],
    linewidth=1.3,
    linestyle="--",
    label="ANT - Typical"
)

plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Speed (km/h)"
)

plt.title(
    "2026 Austrian GP - Selected vs Typical Speed Profiles"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_selected_vs_typical_speed.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ===================================
# 12. Additional comparison
# ===================================

print("\nSELECTED LAP COMPARISON")
print("-----------------------------")

selected_delta = (
    results["ANT"]["strong"]["LapTimeSeconds"]
    - results["RUS"]["strong"]["LapTimeSeconds"]
)

print(
    f"ANT - RUS: "
    f"{selected_delta:+.3f} s"
)

print("\nTYPICAL LAP COMPARISON")
print("-----------------------------")

typical_delta = (
    results["ANT"]["typical"]["LapTimeSeconds"]
    - results["RUS"]["typical"]["LapTimeSeconds"]
)

print(
    f"ANT - RUS: "
    f"{typical_delta:+.3f} s"
)