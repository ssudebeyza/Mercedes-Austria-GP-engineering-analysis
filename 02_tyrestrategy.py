import fastf1
import matplotlib.pyplot as plt

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

# Standard F1 compound colours
compound_colors = {
    "SOFT": "red",
    "MEDIUM": "gold",
    "HARD": "lightgray",
    "INTERMEDIATE": "green",
    "WET": "blue"
}

fig, ax = plt.subplots(figsize=(11, 4))

# -----------------------------------
# 4. Plot each stint
# -----------------------------------
for y_position, driver in enumerate(drivers):

    laps = session.laps.pick_drivers(driver)

    # Group laps by stint
    stints = laps.groupby("Stint")

    for stint_number, stint_laps in stints:

        if stint_laps.empty:
            continue

        # First and last lap of the stint
        start_lap = stint_laps["LapNumber"].min()
        end_lap = stint_laps["LapNumber"].max()

        # Tyre compound
        compounds = stint_laps["Compound"].dropna()

        if compounds.empty:
            compound = "UNKNOWN"
        else:
            compound = compounds.iloc[0]

        color = compound_colors.get(compound, "white")

        # Draw horizontal stint bar
        ax.barh(
            y_position,
            end_lap - start_lap + 1,
            left=start_lap - 1,
            height=0.55,
            color=color,
            edgecolor="black"
        )

        # Add compound label
        ax.text(
            (start_lap + end_lap) / 2,
            y_position,
            f"{compound}",
            ha="center",
            va="center",
            fontsize=9
        )

# -----------------------------------
# 5. Formatting
# -----------------------------------
ax.set_yticks(range(len(drivers)))
ax.set_yticklabels(drivers)

ax.set_xlabel("Lap Number")
ax.set_ylabel("Driver")

ax.set_title("2026 Austrian GP - Tyre Strategy")

ax.grid(
    axis="x",
    alpha=0.3
)

plt.tight_layout()

# -----------------------------------
# 6. Save figure
# -----------------------------------
plt.savefig(
    "2026_austrian_gp_tyre_strategy.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()