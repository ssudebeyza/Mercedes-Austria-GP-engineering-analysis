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

fig, ax = plt.subplots(figsize=(10, 4))

# -----------------------------------
# 4. Find pit-stop laps
# -----------------------------------
for y_position, driver in enumerate(drivers):

    laps = session.laps.pick_drivers(driver)

    # A pit stop is identified by PitInTime
    pit_laps = laps[laps["PitInTime"].notna()]

    for lap_number in pit_laps["LapNumber"]:

        ax.scatter(
            lap_number,
            y_position,
            s=100,
            label=driver if lap_number == pit_laps["LapNumber"].iloc[0] else ""
        )

        ax.text(
            lap_number,
            y_position + 0.12,
            f"Lap {int(lap_number)}",
            ha="center",
            va="bottom",
            fontsize=9
        )

# -----------------------------------
# 5. Formatting
# -----------------------------------
ax.set_yticks(range(len(drivers)))
ax.set_yticklabels(drivers)

ax.set_xlabel("Lap Number")
ax.set_ylabel("Driver")
ax.set_title("2026 Austrian GP - Pit Stop Timeline")

ax.set_xlim(0, session.laps["LapNumber"].max() + 2)

ax.grid(
    axis="x",
    alpha=0.3
)

plt.tight_layout()

# -----------------------------------
# 6. Save figure
# -----------------------------------
plt.savefig(
    "2026_austrian_gp_pit_stop_timeline.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()