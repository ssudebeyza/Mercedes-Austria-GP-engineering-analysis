import fastf1
import matplotlib.pyplot as plt

# -----------------------------------
# 1. FastF1 cache
# -----------------------------------
fastf1.Cache.enable_cache("cache")

# -----------------------------------
# 2. Load 2026 Austrian GP race
# -----------------------------------
session = fastf1.get_session(2026, "Austria", "R")
session.load()

# -----------------------------------
# 3. Select drivers
# -----------------------------------
drivers = ["RUS", "ANT"]

plt.figure(figsize=(10, 5))

# -----------------------------------
# 4. Plot position evolution
# -----------------------------------
for driver in drivers:
    laps = session.laps.pick_drivers(driver)

    plt.step(
        laps["LapNumber"],
        laps["Position"],
        where="post",
        label=driver,
        linewidth=1.8
    )

# -----------------------------------
# 5. Formatting
# -----------------------------------
plt.gca().invert_yaxis()

plt.xlabel("Lap Number")
plt.ylabel("Race Position")
plt.title("2026 Austrian GP - Position Evolution")

plt.yticks(range(1, 21))
plt.grid(alpha=0.3)
plt.legend()

plt.tight_layout()

# -----------------------------------
# 6. Save figure
# -----------------------------------
plt.savefig(
    "2026_austrian_gp_position_evolution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()