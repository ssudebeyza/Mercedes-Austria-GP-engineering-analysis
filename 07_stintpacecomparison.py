import fastf1
import matplotlib.pyplot as plt
import pandas as pd

# -----------------------------------
# 1. Enable FastF1 cache
# -----------------------------------
fastf1.Cache.enable_cache("cache")

# -----------------------------------
# 2. Load 2026 Austrian GP race
# -----------------------------------
session = fastf1.get_session(2026, "Austria", "R")
session.load()

# -----------------------------------
# 3. Drivers
# -----------------------------------
drivers = ["RUS", "ANT"]

stint_results = []

# -----------------------------------
# 4. Process each driver
# -----------------------------------
for driver in drivers:

    laps = session.laps.pick_drivers(driver).copy()

    # Remove invalid lap times
    laps = laps[laps["LapTime"].notna()]

    # Remove pit-in and pit-out laps
    laps = laps[
        laps["PitInTime"].isna()
        & laps["PitOutTime"].isna()
    ]

    # Convert lap time to seconds
    laps["LapTimeSeconds"] = (
        laps["LapTime"].dt.total_seconds()
    )

    # -----------------------------------
    # Representative-lap filter
    # -----------------------------------
    median_time = laps["LapTimeSeconds"].median()

    laps = laps[
        laps["LapTimeSeconds"]
        <= median_time * 1.055
    ].copy()

    # -----------------------------------
    # Analyse each stint separately
    # -----------------------------------
    for stint_number, stint_laps in laps.groupby("Stint"):

        if stint_laps.empty:
            continue

        # Find tyre compound
        compounds = stint_laps["Compound"].dropna()

        if compounds.empty:
            compound = "UNKNOWN"
        else:
            compound = compounds.iloc[0]

        # Calculate stint statistics
        mean_time = (
            stint_laps["LapTimeSeconds"].mean()
        )

        median_time = (
            stint_laps["LapTimeSeconds"].median()
        )

        std_time = (
            stint_laps["LapTimeSeconds"].std()
        )

        lap_count = len(stint_laps)

        # Store results
        stint_results.append({
            "Driver": driver,
            "Stint": int(stint_number),
            "Compound": compound,
            "Mean": mean_time,
            "Median": median_time,
            "Std": std_time,
            "Laps": lap_count
        })

# -----------------------------------
# 5. Convert results to DataFrame
# -----------------------------------
results = pd.DataFrame(stint_results)

results = results.sort_values(
    ["Driver", "Stint"]
)

# -----------------------------------
# 6. Print results
# -----------------------------------
print("\nSTINT PACE SUMMARY")
print("-----------------------------")

print(
    results.to_string(
        index=False
    )
)

# -----------------------------------
# 7. Create labels
# -----------------------------------
labels = []

for _, row in results.iterrows():

    label = (
        f"{row['Driver']} "
        f"S{row['Stint']} "
        f"({row['Compound']})"
    )

    labels.append(label)

# -----------------------------------
# 8. Plot mean stint pace
# -----------------------------------
plt.figure(figsize=(11, 6))

plt.bar(
    labels,
    results["Mean"],
    yerr=results["Std"],
    capsize=4
)

# -----------------------------------
# 9. Formatting
# -----------------------------------
plt.xlabel("Driver / Stint")
plt.ylabel("Mean Representative Lap Time (s)")

plt.title(
    "2026 Austrian GP - Stint Pace Comparison"
)

plt.xticks(
    rotation=30,
    ha="right"
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

# -----------------------------------
# 10. Save
# -----------------------------------
plt.savefig(
    "2026_austrian_gp_stint_pace_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()