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

    laps = laps[
        laps["LapTime"].notna()
    ]

    laps = laps[
        laps["PitInTime"].isna()
        & laps["PitOutTime"].isna()
    ]

    laps["LapTimeSeconds"] = (
        laps["LapTime"]
        .dt
        .total_seconds()
    )

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

    # Elapsed lap time
    telemetry["ElapsedTime"] = (
        telemetry["Time"]
        - telemetry["Time"].iloc[0]
    ).dt.total_seconds()

    # FastF1 Brake is application state,
    # not brake pressure
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
# 7. T6 analysis window
# -----------------------------------
window_start = t6_center - 180
window_end = t6_center + 220

print("\nT6 ANALYSIS WINDOW")
print("-----------------------------")

print(
    f"T6 centre: "
    f"{t6_center:.1f} m"
)

print(
    f"Window: "
    f"{window_start:.1f} m "
    f"to {window_end:.1f} m"
)

# -----------------------------------
# 8. Extract T6 telemetry
# -----------------------------------
t6_data = {}

for driver in ["RUS", "ANT"]:

    telemetry = telemetry_data[
        driver
    ]

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

    t6_data[driver] = corner

# -----------------------------------
# 9. Minimum-speed information
# -----------------------------------
minimum_data = {}

print("\nT6 MINIMUM SPEED")
print("-----------------------------")

for driver in ["RUS", "ANT"]:

    corner = t6_data[driver]

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

    minimum_data[driver] = {
        "speed": min_speed,
        "distance": min_distance
    }

    print(
        f"{driver}: "
        f"{min_speed:.2f} km/h "
        f"at {min_distance:.1f} m"
    )

# -----------------------------------
# 10. Common distance grid
# -----------------------------------
distance_grid = np.linspace(
    window_start,
    window_end,
    2000
)

rus = telemetry_data["RUS"]
ant = telemetry_data["ANT"]

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
# 11. Cumulative delta
# -----------------------------------
# Delta = ANT - RUS
#
# Negative = ANT advantage
# Positive = RUS advantage

raw_delta = (
    ant_elapsed
    - rus_elapsed
)

# Reset delta to zero at T6-window entry
local_delta = (
    raw_delta
    - raw_delta[0]
)

total_t6_delta = (
    local_delta[-1]
)

# -----------------------------------
# 12. Reference minimum-speed point
# -----------------------------------
# Use the mean location of the two
# minimum-speed points as a neutral
# phase boundary.

minimum_reference = np.mean([
    minimum_data["RUS"]["distance"],
    minimum_data["ANT"]["distance"]
])

delta_at_minimum = np.interp(
    minimum_reference,
    distance_grid,
    local_delta
)

# -----------------------------------
# 13. Split T6 gain by phase
# -----------------------------------
entry_to_mid_delta = (
    delta_at_minimum
)

mid_to_exit_delta = (
    total_t6_delta
    - delta_at_minimum
)

if abs(total_t6_delta) > 0:

    entry_to_mid_percentage = (
        abs(entry_to_mid_delta)
        / abs(total_t6_delta)
        * 100
    )

else:

    entry_to_mid_percentage = 0

# -----------------------------------
# 14. Print T6 results
# -----------------------------------
print("\nT6 PERFORMANCE")
print("-----------------------------")

print(
    f"Total T6 delta: "
    f"{total_t6_delta:+.3f} s"
)

print(
    f"Entry-to-mid-corner delta: "
    f"{entry_to_mid_delta:+.3f} s"
)

print(
    f"Mid-corner-to-exit delta: "
    f"{mid_to_exit_delta:+.3f} s"
)

print(
    f"Share developed before "
    f"minimum-speed reference: "
    f"{entry_to_mid_percentage:.1f}%"
)

# -----------------------------------
# 15. Minimum-speed difference
# -----------------------------------
minimum_speed_difference = (
    minimum_data["ANT"]["speed"]
    - minimum_data["RUS"]["speed"]
)

print(
    f"\nMinimum-speed difference "
    f"(ANT - RUS): "
    f"{minimum_speed_difference:+.2f} km/h"
)

# ===================================
# FIGURE 1 - SPEED
# ===================================

plt.figure(
    figsize=(11, 5)
)

for driver in ["RUS", "ANT"]:

    corner = t6_data[driver]

    plt.plot(
        corner["Distance"],
        corner["Speed"],
        linewidth=2,
        label=driver
    )

plt.axvline(
    minimum_reference,
    linestyle="--",
    linewidth=1,
    label="Minimum-Speed Reference"
)

plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Speed (km/h)"
)

plt.title(
    "2026 Austrian GP - T6 Speed Comparison"
)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_t6_speed.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ===================================
# FIGURE 2 - THROTTLE
# ===================================

plt.figure(
    figsize=(11, 5)
)

for driver in ["RUS", "ANT"]:

    corner = t6_data[driver]

    plt.plot(
        corner["Distance"],
        corner["Throttle"],
        linewidth=2,
        label=driver
    )

plt.axvline(
    minimum_reference,
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
    "2026 Austrian GP - T6 Throttle Comparison"
)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_t6_throttle.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ===================================
# FIGURE 3 - BRAKE APPLICATION
# ===================================

plt.figure(
    figsize=(11, 4)
)

for driver in ["RUS", "ANT"]:

    corner = t6_data[driver]

    plt.step(
        corner["Distance"],
        corner["BrakeState"],
        where="post",
        linewidth=1.5,
        label=driver
    )

plt.axvline(
    minimum_reference,
    linestyle="--",
    linewidth=1
)

plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Brake Application"
)

plt.yticks(
    [0, 1],
    ["Off", "On"]
)

plt.ylim(
    -0.1,
    1.2
)

plt.title(
    "2026 Austrian GP - T6 Brake Application"
)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_t6_brake_application.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ===================================
# FIGURE 4 - LOCAL TIME DELTA
# ===================================

plt.figure(
    figsize=(11, 5)
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
    minimum_reference,
    linestyle="--",
    linewidth=1,
    label="Minimum-Speed Reference"
)

plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Local Time Delta (s)"
)

plt.title(
    "2026 Austrian GP - T6 Local Performance Delta"
)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_t6_local_delta.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()