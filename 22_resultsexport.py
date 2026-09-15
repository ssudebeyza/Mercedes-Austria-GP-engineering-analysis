import pandas as pd

# -----------------------------------
# 1. Race-level representative pace
# -----------------------------------
results = [
    {
        "Category": "Representative Pace",
        "Metric": "Mean Lap Time",
        "RUS": 71.868,
        "ANT": 71.825,
        "Unit": "s"
    },
    {
        "Category": "Representative Pace",
        "Metric": "Median Lap Time",
        "RUS": 71.696,
        "ANT": 71.723,
        "Unit": "s"
    },
    {
        "Category": "Representative Pace",
        "Metric": "Standard Deviation",
        "RUS": 0.893,
        "ANT": 1.065,
        "Unit": "s"
    },
    {
        "Category": "Representative Pace",
        "Metric": "Representative Laps",
        "RUS": 64,
        "ANT": 65,
        "Unit": "laps"
    },

    # -----------------------------------
    # Selected representative lap
    # -----------------------------------
    {
        "Category": "Selected Lap",
        "Metric": "Selected Representative Lap",
        "RUS": 70.683,
        "ANT": 70.374,
        "Unit": "s"
    },

    # -----------------------------------
    # Sector medians
    # -----------------------------------
    {
        "Category": "Sector",
        "Metric": "Sector 1 Median",
        "RUS": 17.384,
        "ANT": 17.388,
        "Unit": "s"
    },
    {
        "Category": "Sector",
        "Metric": "Sector 2 Median",
        "RUS": 32.2785,
        "ANT": 32.249,
        "Unit": "s"
    },
    {
        "Category": "Sector",
        "Metric": "Sector 3 Median",
        "RUS": 22.014,
        "ANT": 21.999,
        "Unit": "s"
    },

    # -----------------------------------
    # Stint slopes
    # -----------------------------------
    {
        "Category": "Stint Trend",
        "Metric": "Stint 1 Slope",
        "RUS": 0.028,
        "ANT": 0.026,
        "Unit": "s/lap"
    },
    {
        "Category": "Stint Trend",
        "Metric": "Stint 2 Slope",
        "RUS": 0.044,
        "ANT": 0.028,
        "Unit": "s/lap"
    },
    {
        "Category": "Stint Trend",
        "Metric": "Stint 3 Slope",
        "RUS": 0.012,
        "ANT": -0.061,
        "Unit": "s/lap"
    },

    # -----------------------------------
    # T6
    # -----------------------------------
    {
        "Category": "T6",
        "Metric": "Minimum Speed",
        "RUS": 161.08,
        "ANT": 163.00,
        "Unit": "km/h"
    },
    {
        "Category": "T6",
        "Metric": "D50 After Minimum Speed",
        "RUS": 30,
        "ANT": 24,
        "Unit": "m"
    },
    {
        "Category": "T6",
        "Metric": "D90 After Minimum Speed",
        "RUS": 70,
        "ANT": 64,
        "Unit": "m"
    },
    {
        "Category": "T6",
        "Metric": "Brake Release to D50",
        "RUS": 86,
        "ANT": 74,
        "Unit": "m"
    },

    # -----------------------------------
    # T10
    # -----------------------------------
    {
        "Category": "T10",
        "Metric": "Minimum Speed",
        "RUS": 161.10,
        "ANT": 164.13,
        "Unit": "km/h"
    }
]

# -----------------------------------
# 2. Create DataFrame
# -----------------------------------
df = pd.DataFrame(results)

# -----------------------------------
# 3. Calculate ANT - RUS delta
# -----------------------------------
df["ANT_minus_RUS"] = (
    df["ANT"] - df["RUS"]
)

# -----------------------------------
# 4. Print results
# -----------------------------------
print("\n2026 AUSTRIAN GP")
print("PERFORMANCE ENGINEERING SUMMARY")
print("-----------------------------------")

print(
    df.to_string(
        index=False
    )
)

# -----------------------------------
# 5. Export main KPI table
# -----------------------------------
df.to_csv(
    "2026_austrian_gp_performance_summary.csv",
    index=False
)

# ===================================
# 6. CORNER DELTA TABLE
# ===================================

# Delta = ANT - RUS
#
# Negative = ANT advantage
# Positive = RUS advantage

corner_data = [
    {
        "Corner": "T1",
        "Delta_ANT_minus_RUS_s": -0.067
    },
    {
        "Corner": "T3",
        "Delta_ANT_minus_RUS_s": -0.042
    },
    {
        "Corner": "T4",
        "Delta_ANT_minus_RUS_s": 0.013
    },
    {
        "Corner": "T6",
        "Delta_ANT_minus_RUS_s": -0.145
    },
    {
        "Corner": "T7",
        "Delta_ANT_minus_RUS_s": 0.009
    },
    {
        "Corner": "T9",
        "Delta_ANT_minus_RUS_s": -0.025
    },
    {
        "Corner": "T10",
        "Delta_ANT_minus_RUS_s": -0.047
    }
]

corner_df = pd.DataFrame(
    corner_data
)

# -----------------------------------
# 7. Add advantage column
# -----------------------------------
corner_df["Advantage"] = (
    corner_df[
        "Delta_ANT_minus_RUS_s"
    ].apply(
        lambda delta:
        "ANT"
        if delta < 0
        else "RUS"
    )
)

# -----------------------------------
# 8. Print corner results
# -----------------------------------
print("\nCORNER PERFORMANCE")
print("-----------------------------------")

print(
    corner_df.to_string(
        index=False
    )
)

# -----------------------------------
# 9. Export corner results
# -----------------------------------
corner_df.to_csv(
    "2026_austrian_gp_corner_deltas.csv",
    index=False
)

# -----------------------------------
# 10. Final message
# -----------------------------------
print(
    "\nFiles created:"
)

print(
    "2026_austrian_gp_performance_summary.csv"
)

print(
    "2026_austrian_gp_corner_deltas.csv"
)