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
# 4. Get selected-lap telemetry
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

    # Find selected representative lap
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

    # Get telemetry
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

    # Elapsed time
    telemetry["ElapsedTime"] = (
        telemetry["Time"]
        - telemetry["Time"].iloc[0]
    ).dt.total_seconds()

    # Binary brake state
    telemetry["BrakeState"] = (
        telemetry["Brake"]
        .astype(int)
    )

    # Clean distance
    telemetry = telemetry.drop_duplicates(
        subset="Distance"
    )

    telemetry = telemetry.sort_values(
        "Distance"
    )

    telemetry_data[driver] = telemetry

# -----------------------------------
# 5. Find Turn 3 location
# -----------------------------------
circuit_info = session.get_circuit_info()

corners = circuit_info.corners

t3_row = corners[
    corners["Number"] == 3
]

t3_center = float(
    t3_row["Distance"].iloc[0]
)

print(
    f"\nT3 centre: "
    f"{t3_center:.1f} m"
)

# -----------------------------------
# 6. Define T3 analysis window
# -----------------------------------
window_start = (
    t3_center - 180
)

window_end = (
    t3_center + 220
)

print(
    f"T3 window: "
    f"{window_start:.1f} m - "
    f"{window_end:.1f} m"
)

# -----------------------------------
# 7. Extract T3 telemetry
# -----------------------------------
t3_data = {}

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

    t3_data[driver] = corner

# -----------------------------------
# 8. Minimum speed
# -----------------------------------
print("\nT3 MINIMUM SPEED")
print("-----------------------------")

for driver in ["RUS", "ANT"]:

    corner = t3_data[driver]

    min_index = (
        corner["Speed"].idxmin()
    )

    min_speed = corner.loc[
        min_index,
        "Speed"
    ]

    min_distance = corner.loc[
        min_index,
        "Distance"
    ]

    print(
        f"{driver}: "
        f"{min_speed:.1f} km/h "
        f"at {min_distance:.1f} m"
    )

# -----------------------------------
# 9. Calculate T3 time delta
# -----------------------------------
distance_grid = np.linspace(
    window_start,
    window_end,
    1500
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

# Delta = ANT - RUS
delta = (
    ant_elapsed
    - rus_elapsed
)

# Remove delta already present
# before entering T3 window
local_delta = (
    delta
    - delta[0]
)

t3_delta = local_delta[-1]

print("\nT3 PERFORMANCE DELTA")
print("-----------------------------")

print(
    f"ANT - RUS: "
    f"{t3_delta:+.3f} s"
)

if t3_delta < 0:

    print(
        f"ANT advantage: "
        f"{abs(t3_delta):.3f} s"
    )

else:

    print(
        f"RUS advantage: "
        f"{abs(t3_delta):.3f} s"
    )

# -----------------------------------
# 10. SPEED PLOT
# -----------------------------------
plt.figure(
    figsize=(11, 5)
)

for driver in ["RUS", "ANT"]:

    corner = t3_data[driver]

    plt.plot(
        corner["Distance"],
        corner["Speed"],
        linewidth=2,
        label=driver
    )

plt.axvline(
    t3_center,
    linestyle="--",
    linewidth=1,
    label="T3 Reference"
)

plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Speed (km/h)"
)

plt.title(
    "2026 Austrian GP - T3 Speed Comparison"
)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_t3_speed.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# -----------------------------------
# 11. THROTTLE PLOT
# -----------------------------------
plt.figure(
    figsize=(11, 5)
)

for driver in ["RUS", "ANT"]:

    corner = t3_data[driver]

    plt.plot(
        corner["Distance"],
        corner["Throttle"],
        linewidth=2,
        label=driver
    )

plt.axvline(
    t3_center,
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
    "2026 Austrian GP - T3 Throttle Comparison"
)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_t3_throttle.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# -----------------------------------
# 12. BRAKE APPLICATION PLOT
# -----------------------------------
plt.figure(
    figsize=(11, 4)
)

for driver in ["RUS", "ANT"]:

    corner = t3_data[driver]

    plt.step(
        corner["Distance"],
        corner["BrakeState"],
        where="post",
        linewidth=1.5,
        label=driver
    )

plt.axvline(
    t3_center,
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
    "2026 Austrian GP - T3 Brake Application"
)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_t3_brake_application.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# -----------------------------------
# 13. LOCAL DELTA PLOT
# -----------------------------------
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
    t3_center,
    linestyle="--",
    linewidth=1
)

plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Local Time Delta (s)"
)

plt.title(
    "2026 Austrian GP - T3 Local Performance Delta"
)

plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_t3_local_delta.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()