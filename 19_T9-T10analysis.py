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
# 4. Find selected laps
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
        [
            "Distance",
            "Time",
            "Speed",
            "Throttle",
            "Brake"
        ]
    ].dropna().copy()

    telemetry["ElapsedTime"] = (
        telemetry["Time"]
        - telemetry["Time"].iloc[0]
    ).dt.total_seconds()

    # Brake is binary application state
    telemetry["BrakeState"] = (
        telemetry["Brake"]
        .astype(int)
    )

    telemetry = telemetry.drop_duplicates(
        subset="Distance"
    )

    telemetry = telemetry.sort_values(
        "Distance"
    )

    telemetry_data[driver] = telemetry

# -----------------------------------
# 6. Get T9 and T10 locations
# -----------------------------------
circuit_info = session.get_circuit_info()

corners = circuit_info.corners

t9_row = corners[
    corners["Number"] == 9
]

t10_row = corners[
    corners["Number"] == 10
]

t9_center = float(
    t9_row["Distance"].iloc[0]
)

t10_center = float(
    t10_row["Distance"].iloc[0]
)

print("\nCORNER LOCATIONS")
print("-----------------------------")

print(
    f"T9 centre: {t9_center:.1f} m"
)

print(
    f"T10 centre: {t10_center:.1f} m"
)

# -----------------------------------
# 7. Define sequence window
# -----------------------------------
sequence_start = (
    t9_center - 180
)

sequence_end = (
    t10_center + 220
)

# Midpoint used to split T9 / T10
transition_point = (
    t9_center + t10_center
) / 2

print(
    f"Sequence window: "
    f"{sequence_start:.1f} - "
    f"{sequence_end:.1f} m"
)

# -----------------------------------
# 8. Common distance grid
# -----------------------------------
distance_grid = np.linspace(
    sequence_start,
    sequence_end,
    2500
)

rus = telemetry_data["RUS"]
ant = telemetry_data["ANT"]

# -----------------------------------
# 9. Interpolate elapsed time
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
# 10. Calculate local delta
# -----------------------------------
# Delta = ANT - RUS
#
# Negative = ANT advantage
# Positive = RUS advantage

raw_delta = (
    ant_elapsed
    - rus_elapsed
)

# Reset at sequence entry
local_delta = (
    raw_delta
    - raw_delta[0]
)

# -----------------------------------
# 11. Split T9 and T10
# -----------------------------------
delta_transition = np.interp(
    transition_point,
    distance_grid,
    local_delta
)

final_delta = (
    local_delta[-1]
)

t9_delta = (
    delta_transition
)

t10_delta = (
    final_delta
    - delta_transition
)

print("\nT9-T10 PERFORMANCE")
print("-----------------------------")

print(
    f"T9 section delta: "
    f"{t9_delta:+.3f} s"
)

print(
    f"T10 section delta: "
    f"{t10_delta:+.3f} s"
)

print(
    f"Combined T9-T10 delta: "
    f"{final_delta:+.3f} s"
)

# -----------------------------------
# 12. Extract sequence telemetry
# -----------------------------------
sequence_data = {}

for driver in ["RUS", "ANT"]:

    telemetry = telemetry_data[
        driver
    ]

    sequence = telemetry[
        (
            telemetry["Distance"]
            >= sequence_start
        )
        &
        (
            telemetry["Distance"]
            <= sequence_end
        )
    ].copy()

    sequence_data[driver] = sequence

# -----------------------------------
# 13. Extract T10 telemetry
# -----------------------------------
t10_start = transition_point
t10_end = sequence_end

t10_data = {}

for driver in ["RUS", "ANT"]:

    telemetry = telemetry_data[
        driver
    ]

    corner = telemetry[
        (
            telemetry["Distance"]
            >= t10_start
        )
        &
        (
            telemetry["Distance"]
            <= t10_end
        )
    ].copy()

    t10_data[driver] = corner

# -----------------------------------
# 14. T10 minimum speed
# -----------------------------------
t10_results = {}

print("\nT10 MINIMUM SPEED")
print("-----------------------------")

for driver in ["RUS", "ANT"]:

    corner = t10_data[driver]

    min_index = (
        corner["Speed"].idxmin()
    )

    min_speed = float(
        corner.loc[
            min_index,
            "Speed"
        ]
    )

    min_distance = float(
        corner.loc[
            min_index,
            "Distance"
        ]
    )

    t10_results[driver] = {
        "min_speed": min_speed,
        "min_distance": min_distance
    }

    print(
        f"{driver}: "
        f"{min_speed:.2f} km/h "
        f"at {min_distance:.1f} m"
    )

# -----------------------------------
# 15. Minimum-speed difference
# -----------------------------------
speed_difference = (
    t10_results["ANT"]["min_speed"]
    - t10_results["RUS"]["min_speed"]
)

print(
    f"\nT10 minimum-speed difference "
    f"(ANT - RUS): "
    f"{speed_difference:+.2f} km/h"
)

# -----------------------------------
# 16. Find 90% throttle point
# -----------------------------------
for driver in ["RUS", "ANT"]:

    corner = t10_data[driver]

    min_distance = (
        t10_results[driver][
            "min_distance"
        ]
    )

    # Only look after minimum speed
    after_minimum = corner[
        corner["Distance"]
        >= min_distance
    ].copy()

    throttle_90 = after_minimum[
        after_minimum["Throttle"] >= 90
    ]

    if not throttle_90.empty:

        d90_absolute = float(
            throttle_90[
                "Distance"
            ].iloc[0]
        )

        d90 = (
            d90_absolute
            - min_distance
        )

    else:

        d90_absolute = np.nan
        d90 = np.nan

    t10_results[driver][
        "d90_absolute"
    ] = d90_absolute

    t10_results[driver][
        "d90"
    ] = d90

# -----------------------------------
# 17. Print throttle recovery
# -----------------------------------
print("\nT10 THROTTLE RECOVERY")
print("-----------------------------")

for driver in ["RUS", "ANT"]:

    print(
        f"{driver} D90: "
        f"{t10_results[driver]['d90']:.1f} m "
        f"after minimum speed"
    )

d90_difference = (
    t10_results["ANT"]["d90"]
    - t10_results["RUS"]["d90"]
)

print(
    f"\nD90 difference "
    f"(ANT - RUS): "
    f"{d90_difference:+.1f} m"
)

# ===================================
# FIGURE 1 - SPEED
# ===================================

plt.figure(
    figsize=(12, 5)
)

for driver in ["RUS", "ANT"]:

    sequence = sequence_data[
        driver
    ]

    plt.plot(
        sequence["Distance"],
        sequence["Speed"],
        linewidth=2,
        label=driver
    )

plt.axvline(
    t9_center,
    linestyle="--",
    linewidth=1,
    label="T9"
)

plt.axvline(
    t10_center,
    linestyle=":",
    linewidth=1,
    label="T10"
)

plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Speed (km/h)"
)

plt.title(
    "2026 Austrian GP - T9-T10 Speed Comparison"
)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_t9_t10_speed.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ===================================
# FIGURE 2 - THROTTLE
# ===================================

plt.figure(
    figsize=(12, 5)
)

for driver in ["RUS", "ANT"]:

    sequence = sequence_data[
        driver
    ]

    plt.plot(
        sequence["Distance"],
        sequence["Throttle"],
        linewidth=2,
        label=driver
    )

plt.axhline(
    90,
    linestyle="--",
    linewidth=1
)

plt.axvline(
    t9_center,
    linestyle="--",
    linewidth=1
)

plt.axvline(
    t10_center,
    linestyle=":",
    linewidth=1
)

plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Throttle (%)"
)

plt.title(
    "2026 Austrian GP - T9-T10 Throttle Comparison"
)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_t9_t10_throttle.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ===================================
# FIGURE 3 - LOCAL DELTA
# ===================================

plt.figure(
    figsize=(12, 5)
)

plt.plot(
    distance_grid,
    local_delta,
    linewidth=2
)

plt.axhline(
    0,
    linestyle="--",
    linewidth=1
)

plt.axvline(
    t9_center,
    linestyle="--",
    linewidth=1,
    label="T9"
)

plt.axvline(
    t10_center,
    linestyle=":",
    linewidth=1,
    label="T10"
)

plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Local Time Delta (s)"
)

plt.title(
    "2026 Austrian GP - T9-T10 Local Performance Delta"
)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_t9_t10_local_delta.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ===================================
# FIGURE 4 - T10 D90
# ===================================

plt.figure(
    figsize=(10, 5)
)

for driver in ["RUS", "ANT"]:

    corner = t10_data[
        driver
    ]

    plt.plot(
        corner["Distance"],
        corner["Throttle"],
        linewidth=2,
        label=driver
    )

    d90_absolute = (
        t10_results[driver][
            "d90_absolute"
        ]
    )

    if not np.isnan(
        d90_absolute
    ):

        plt.scatter(
            d90_absolute,
            90,
            s=60
        )

plt.axhline(
    90,
    linestyle="--",
    linewidth=1
)

plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Throttle (%)"
)

plt.title(
    "2026 Austrian GP - T10 Throttle Recovery"
)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_t10_throttle_recovery.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()