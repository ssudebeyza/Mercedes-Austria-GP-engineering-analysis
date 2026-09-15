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
selected_times = {}

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

    selected_times[driver] = float(
        selected_lap["LapTimeSeconds"]
    )

    print(
        f"{driver}: "
        f"Lap {int(selected_lap['LapNumber'])} - "
        f"{selected_times[driver]:.3f} s"
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
            "Speed"
        ]
    ].dropna().copy()

    # Elapsed time
    telemetry["ElapsedTime"] = (
        telemetry["Time"]
        - telemetry["Time"].iloc[0]
    ).dt.total_seconds()

    # Clean distance
    telemetry = telemetry.drop_duplicates(
        subset="Distance"
    )

    telemetry = telemetry.sort_values(
        "Distance"
    )

    telemetry_data[driver] = telemetry

# -----------------------------------
# 6. Common distance range
# -----------------------------------
rus = telemetry_data["RUS"]
ant = telemetry_data["ANT"]

start_distance = max(
    rus["Distance"].min(),
    ant["Distance"].min()
)

end_distance = min(
    rus["Distance"].max(),
    ant["Distance"].max()
)

distance_grid = np.linspace(
    start_distance,
    end_distance,
    5000
)

# -----------------------------------
# 7. Interpolate elapsed time
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
# 8. Calculate incremental time
# -----------------------------------
rus_dt = np.diff(
    rus_elapsed,
    prepend=rus_elapsed[0]
)

ant_dt = np.diff(
    ant_elapsed,
    prepend=ant_elapsed[0]
)

# -----------------------------------
# 9. Build exploratory envelope
# -----------------------------------
# At each distance interval, retain
# the smaller observed elapsed-time
# increment from the two selected laps.
#
# This is an analytical envelope only.
# It is NOT a physically validated
# "perfect lap".

envelope_dt = np.minimum(
    rus_dt,
    ant_dt
)

envelope_elapsed = np.cumsum(
    envelope_dt
)

# Reset to zero
envelope_elapsed = (
    envelope_elapsed
    - envelope_elapsed[0]
)

# -----------------------------------
# 10. Calculate estimates
# -----------------------------------
envelope_time = (
    envelope_elapsed[-1]
)

rus_telemetry_time = (
    rus_elapsed[-1]
    - rus_elapsed[0]
)

ant_telemetry_time = (
    ant_elapsed[-1]
    - ant_elapsed[0]
)

rus_potential = (
    rus_telemetry_time
    - envelope_time
)

ant_potential = (
    ant_telemetry_time
    - envelope_time
)

# -----------------------------------
# 11. Print results
# -----------------------------------
print("\nTHEORETICAL PERFORMANCE ENVELOPE")
print("--------------------------------")

print(
    f"RUS telemetry time: "
    f"{rus_telemetry_time:.3f} s"
)

print(
    f"ANT telemetry time: "
    f"{ant_telemetry_time:.3f} s"
)

print(
    f"Exploratory envelope: "
    f"{envelope_time:.3f} s"
)

print(
    f"RUS difference to envelope: "
    f"{rus_potential:.3f} s"
)

print(
    f"ANT difference to envelope: "
    f"{ant_potential:.3f} s"
)

# -----------------------------------
# 12. Plot elapsed-time traces
# -----------------------------------
plt.figure(
    figsize=(12, 6)
)

plt.plot(
    distance_grid,
    rus_elapsed - rus_elapsed[0],
    linewidth=1.5,
    label="RUS Selected"
)

plt.plot(
    distance_grid,
    ant_elapsed - ant_elapsed[0],
    linewidth=1.5,
    label="ANT Selected"
)

plt.plot(
    distance_grid,
    envelope_elapsed,
    linewidth=2.5,
    linestyle="--",
    label="Theoretical Envelope"
)

# -----------------------------------
# 13. Formatting
# -----------------------------------
plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Elapsed Time (s)"
)

plt.title(
    "2026 Austrian GP - Theoretical Performance Envelope"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

# -----------------------------------
# 14. Save
# -----------------------------------
plt.savefig(
    "2026_austrian_gp_theoretical_performance_envelope.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()