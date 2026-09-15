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
# 3. Drivers
# -----------------------------------
drivers = ["RUS", "ANT"]

# Selected representative lap times
# used in the report
target_times = {
    "RUS": 70.683,
    "ANT": 70.374
}

selected_laps = {}

# -----------------------------------
# 4. Find selected laps
# -----------------------------------
for driver in drivers:

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

    # Convert to seconds
    laps["LapTimeSeconds"] = (
        laps["LapTime"]
        .dt
        .total_seconds()
    )

    # -----------------------------------
    # Find lap closest to target time
    # -----------------------------------
    target = target_times[driver]

    difference = (
        laps["LapTimeSeconds"]
        - target
    ).abs()

    selected_index = difference.idxmin()

    selected_lap = laps.loc[
        selected_index
    ]

    selected_laps[driver] = selected_lap

    # -----------------------------------
    # Print selected lap
    # -----------------------------------
    print(f"\n{driver}")
    print("----------------------")

    print(
        f"Lap Number: "
        f"{int(selected_lap['LapNumber'])}"
    )

    print(
        f"Lap Time: "
        f"{selected_lap['LapTimeSeconds']:.3f} s"
    )

# -----------------------------------
# 5. Calculate selected-lap delta
# -----------------------------------
rus_time = (
    selected_laps["RUS"][
        "LapTimeSeconds"
    ]
)

ant_time = (
    selected_laps["ANT"][
        "LapTimeSeconds"
    ]
)

delta = ant_time - rus_time

print("\nSELECTED-LAP COMPARISON")
print("----------------------")

print(
    f"RUS: {rus_time:.3f} s"
)

print(
    f"ANT: {ant_time:.3f} s"
)

print(
    f"ANT - RUS: {delta:+.3f} s"
)

# -----------------------------------
# 6. Plot
# -----------------------------------
times = [
    rus_time,
    ant_time
]

plt.figure(
    figsize=(7, 5)
)

bars = plt.bar(
    drivers,
    times
)

# -----------------------------------
# 7. Add values above bars
# -----------------------------------
for bar, time in zip(
    bars,
    times
):

    plt.text(
        bar.get_x()
        + bar.get_width() / 2,

        time + 0.02,

        f"{time:.3f} s",

        ha="center",
        va="bottom"
    )

# -----------------------------------
# 8. Formatting
# -----------------------------------
plt.xlabel(
    "Driver"
)

plt.ylabel(
    "Selected Representative Lap Time (s)"
)

plt.title(
    "2026 Austrian GP - Selected Representative Laps"
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

# -----------------------------------
# 9. Save
# -----------------------------------
plt.savefig(
    "2026_austrian_gp_selected_representative_laps.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()