import fastf1
import matplotlib.pyplot as plt

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
    # 5. Find lap closest to target
    # -----------------------------------
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
    # 6. Get telemetry
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

    # Convert brake state to integer
    telemetry["BrakeState"] = (
        telemetry["Brake"]
        .astype(int)
    )

    telemetry_data[driver] = telemetry

# -----------------------------------
# 7. Plot brake application
# -----------------------------------
plt.figure(
    figsize=(12, 5)
)

for driver in ["RUS", "ANT"]:

    telemetry = telemetry_data[
        driver
    ]

    plt.step(
        telemetry["Distance"],
        telemetry["BrakeState"],
        where="post",
        linewidth=1.5,
        label=driver
    )

# -----------------------------------
# 8. Formatting
# -----------------------------------
plt.xlabel(
    "Distance Around Lap (m)"
)

plt.ylabel(
    "Brake Application"
)

plt.title(
    "2026 Austrian GP - Brake Application"
)

plt.yticks(
    [0, 1],
    ["Off", "On"]
)

plt.ylim(
    -0.1,
    1.2
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

# -----------------------------------
# 9. Save
# -----------------------------------
plt.savefig(
    "2026_austrian_gp_brake_application.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()