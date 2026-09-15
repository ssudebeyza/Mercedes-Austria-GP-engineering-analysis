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
# 4. Find selected laps
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

    # Find lap closest to target
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
            "Speed",
            "Throttle",
            "Brake"
        ]
    ].dropna().copy()

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
# 6. Find T6 centre
# -----------------------------------
circuit_info = session.get_circuit_info()

corners = circuit_info.corners

t6_row = corners[
    corners["Number"] == 6
]

t6_center = float(
    t6_row["Distance"].iloc[0]
)

# -----------------------------------
# 7. Define T6 window
# -----------------------------------
window_start = t6_center - 180
window_end = t6_center + 220

print("\nT6 WINDOW")
print("-----------------------------")

print(
    f"Centre: {t6_center:.1f} m"
)

print(
    f"Window: "
    f"{window_start:.1f} - "
    f"{window_end:.1f} m"
)

# -----------------------------------
# 8. Analysis function
# -----------------------------------
def analyse_throttle(driver):

    telemetry = telemetry_data[
        driver
    ]

    # Extract T6 window
    corner = telemetry[
        (
            telemetry["Distance"]
            >= window_start
        )
        &
        (
            telemetry["Distance"]
            <= window_end
        )
    ].copy()

    # -----------------------------------
    # Minimum-speed point
    # -----------------------------------
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

    # -----------------------------------
    # Data after minimum speed
    # -----------------------------------
    after_min = corner[
        corner["Distance"]
        >= min_distance
    ].copy()

    # -----------------------------------
    # D50
    # First point >= 50% throttle
    # after minimum speed
    # -----------------------------------
    throttle_50 = after_min[
        after_min["Throttle"] >= 50
    ]

    if not throttle_50.empty:

        d50_absolute = float(
            throttle_50[
                "Distance"
            ].iloc[0]
        )

        d50 = (
            d50_absolute
            - min_distance
        )

    else:

        d50_absolute = np.nan
        d50 = np.nan

    # -----------------------------------
    # D90
    # First point >= 90% throttle
    # after minimum speed
    # -----------------------------------
    throttle_90 = after_min[
        after_min["Throttle"] >= 90
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

    # -----------------------------------
    # Brake release
    # -----------------------------------
    before_min = corner[
        corner["Distance"]
        <= min_distance
    ].copy()

    braking = before_min[
        before_min["BrakeState"] == 1
    ]

    if not braking.empty:

        brake_release_distance = float(
            braking[
                "Distance"
            ].iloc[-1]
        )

    else:

        brake_release_distance = np.nan

    # -----------------------------------
    # Brake release -> D50
    # -----------------------------------
    if (
        not np.isnan(
            brake_release_distance
        )
        and
        not np.isnan(
            d50_absolute
        )
    ):

        brake_to_d50 = (
            d50_absolute
            - brake_release_distance
        )

    else:

        brake_to_d50 = np.nan

    return {
        "corner": corner,
        "min_speed": min_speed,
        "min_distance": min_distance,
        "d50": d50,
        "d90": d90,
        "d50_absolute": d50_absolute,
        "d90_absolute": d90_absolute,
        "brake_release": brake_release_distance,
        "brake_to_d50": brake_to_d50
    }

# -----------------------------------
# 9. Run analysis
# -----------------------------------
results = {}

for driver in ["RUS", "ANT"]:

    results[driver] = (
        analyse_throttle(driver)
    )

# -----------------------------------
# 10. Print results
# -----------------------------------
print("\nT6 THROTTLE RECOVERY")
print("-----------------------------")

for driver in ["RUS", "ANT"]:

    result = results[driver]

    print(f"\n{driver}")

    print(
        f"Minimum speed: "
        f"{result['min_speed']:.2f} km/h"
    )

    print(
        f"Minimum-speed location: "
        f"{result['min_distance']:.1f} m"
    )

    print(
        f"D50 after minimum speed: "
        f"{result['d50']:.1f} m"
    )

    print(
        f"D90 after minimum speed: "
        f"{result['d90']:.1f} m"
    )

    print(
        f"Brake release -> D50: "
        f"{result['brake_to_d50']:.1f} m"
    )

# -----------------------------------
# 11. Compare drivers
# -----------------------------------
print("\nDRIVER DIFFERENCE")
print("-----------------------------")

print(
    "D50 ANT - RUS: "
    f"{results['ANT']['d50'] - results['RUS']['d50']:+.1f} m"
)

print(
    "D90 ANT - RUS: "
    f"{results['ANT']['d90'] - results['RUS']['d90']:+.1f} m"
)

print(
    "Brake-to-D50 ANT - RUS: "
    f"{results['ANT']['brake_to_d50'] - results['RUS']['brake_to_d50']:+.1f} m"
)

# -----------------------------------
# 12. Throttle plot
# -----------------------------------
plt.figure(
    figsize=(11, 5)
)

for driver in ["RUS", "ANT"]:

    result = results[driver]
    corner = result["corner"]

    plt.plot(
        corner["Distance"],
        corner["Throttle"],
        linewidth=2,
        label=driver
    )

    # D50 marker
    if not np.isnan(
        result["d50_absolute"]
    ):

        plt.scatter(
            result["d50_absolute"],
            50,
            s=60
        )

    # D90 marker
    if not np.isnan(
        result["d90_absolute"]
    ):

        plt.scatter(
            result["d90_absolute"],
            90,
            s=60
        )

# -----------------------------------
# 13. Reference lines
# -----------------------------------
plt.axhline(
    50,
    linestyle="--",
    linewidth=1
)

plt.axhline(
    90,
    linestyle="--",
    linewidth=1
)

plt.axvline(
    t6_center,
    linestyle="--",
    linewidth=1
)

# -----------------------------------
# 14. Formatting
# -----------------------------------
plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Throttle (%)"
)

plt.title(
    "2026 Austrian GP - T6 Throttle Recovery"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

# -----------------------------------
# 15. Save
# -----------------------------------
plt.savefig(
    "2026_austrian_gp_t6_throttle_recovery.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()