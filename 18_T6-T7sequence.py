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

    # Valid laps
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

    # Elapsed lap time
    telemetry["ElapsedTime"] = (
        telemetry["Time"]
        - telemetry["Time"].iloc[0]
    ).dt.total_seconds()

    # Binary brake application
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
# 5. Circuit information
# -----------------------------------
circuit_info = session.get_circuit_info()

corners = circuit_info.corners

# T6
t6_row = corners[
    corners["Number"] == 6
]

t6_center = float(
    t6_row["Distance"].iloc[0]
)

# T7
t7_row = corners[
    corners["Number"] == 7
]

t7_center = float(
    t7_row["Distance"].iloc[0]
)

# -----------------------------------
# 6. Define T6-T7 sequence window
# -----------------------------------
sequence_start = (
    t6_center - 180
)

sequence_end = (
    t7_center + 180
)

print("\nT6-T7 SEQUENCE")
print("-----------------------------")

print(
    f"T6 centre: "
    f"{t6_center:.1f} m"
)

print(
    f"T7 centre: "
    f"{t7_center:.1f} m"
)

print(
    f"Sequence: "
    f"{sequence_start:.1f} - "
    f"{sequence_end:.1f} m"
)

# -----------------------------------
# 7. Common distance grid
# -----------------------------------
distance_grid = np.linspace(
    sequence_start,
    sequence_end,
    2500
)

rus = telemetry_data["RUS"]
ant = telemetry_data["ANT"]

# -----------------------------------
# 8. Interpolate elapsed time
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
# 9. Local cumulative delta
# -----------------------------------
# Delta = ANT - RUS
#
# Negative = ANT advantage
# Positive = RUS advantage

raw_delta = (
    ant_elapsed
    - rus_elapsed
)

# Reset to zero at sequence entry
local_delta = (
    raw_delta
    - raw_delta[0]
)

# -----------------------------------
# 10. Define T6 end / T7 start
# -----------------------------------
# Midpoint between official corner
# reference positions is used only
# as a simple sequence boundary.

transition_point = (
    t6_center
    + t7_center
) / 2

delta_at_transition = np.interp(
    transition_point,
    distance_grid,
    local_delta
)

final_sequence_delta = (
    local_delta[-1]
)

# Change through T7-side section
t7_section_delta = (
    final_sequence_delta
    - delta_at_transition
)

# -----------------------------------
# 11. Print delta results
# -----------------------------------
print("\nSEQUENCE PERFORMANCE")
print("-----------------------------")

print(
    f"Delta at T6-T7 transition: "
    f"{delta_at_transition:+.3f} s"
)

print(
    f"Change through T7 section: "
    f"{t7_section_delta:+.3f} s"
)

print(
    f"Final T6-T7 sequence delta: "
    f"{final_sequence_delta:+.3f} s"
)

if final_sequence_delta < 0:

    print(
        f"Net sequence advantage: "
        f"ANT by "
        f"{abs(final_sequence_delta):.3f} s"
    )

else:

    print(
        f"Net sequence advantage: "
        f"RUS by "
        f"{abs(final_sequence_delta):.3f} s"
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
    t6_center,
    linestyle="--",
    linewidth=1,
    label="T6"
)

plt.axvline(
    t7_center,
    linestyle=":",
    linewidth=1,
    label="T7"
)

plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Speed (km/h)"
)

plt.title(
    "2026 Austrian GP - T6-T7 Speed Comparison"
)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_t6_t7_speed.png",
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

plt.axvline(
    t6_center,
    linestyle="--",
    linewidth=1
)

plt.axvline(
    t7_center,
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
    "2026 Austrian GP - T6-T7 Throttle Comparison"
)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_t6_t7_throttle.png",
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
    t6_center,
    linestyle="--",
    linewidth=1,
    label="T6"
)

plt.axvline(
    t7_center,
    linestyle=":",
    linewidth=1,
    label="T7"
)

plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Local Time Delta (s)"
)

plt.title(
    "2026 Austrian GP - T6-T7 Sequence Delta"
)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "2026_austrian_gp_t6_t7_sequence_delta.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()