from pathlib import Path
import subprocess
import sys
import time


# ===================================
# PROJECT CONFIGURATION
# ===================================

PROJECT_ROOT = Path(__file__).resolve().parent

CACHE_DIRECTORY = PROJECT_ROOT / "cache"

STOP_ON_ERROR = True


# ===================================
# ANALYSIS SCRIPTS
# ===================================

SCRIPTS = [
    "01_position_evolution.py",
    "02_tyre_strategy.py",
    "03_pit_stop_timeline.py",
    "04_lap_time_evolution.py",
    "05_five_lap_moving_average.py",
    "06_pace_distribution.py",
    "07_stint_pace_comparison.py",
    "08_stint_pace_trendlines.py",
    "09_sector_pace_comparison.py",
    "10_selected_representative_laps.py",
    "11_cumulative_lap_delta.py",
    "12_corner_deltas.py",
    "13_corner_loss_map.py",
    "14_brake_application.py",
    "15_t3_analysis.py",
    "16_t6_analysis.py",
    "17_t6_throttle_analysis.py",
    "18_t6_t7_sequence.py",
    "19_t9_t10_analysis.py",
    "20_best_vs_typical.py",
    "21_theoretical_performance_envelope.py",
    "22_results_export.py",
]


# ===================================
# CREATE PROJECT DIRECTORIES
# ===================================

def create_directories():

    CACHE_DIRECTORY.mkdir(
        exist_ok=True
    )

    print(
        f"FastF1 cache directory: "
        f"{CACHE_DIRECTORY}"
    )


# ===================================
# RUN ONE SCRIPT
# ===================================

def run_script(
    script_name
):

    script_path = (
        PROJECT_ROOT
        / script_name
    )

    # Check that script exists
    if not script_path.exists():

        print(
            f"\n[ERROR] "
            f"{script_name} not found."
        )

        return False

    print("\n")
    print("=" * 65)

    print(
        f"Running: "
        f"{script_name}"
    )

    print("=" * 65)

    start_time = time.time()

    try:

        subprocess.run(
            [
                sys.executable,
                str(script_path)
            ],
            cwd=PROJECT_ROOT,
            check=True
        )

        elapsed = (
            time.time()
            - start_time
        )

        print(
            f"\nCompleted "
            f"{script_name}"
        )

        print(
            f"Execution time: "
            f"{elapsed:.1f} s"
        )

        return True

    except subprocess.CalledProcessError:

        print(
            f"\n[ERROR] "
            f"{script_name} failed."
        )

        return False


# ===================================
# MAIN ANALYSIS PIPELINE
# ===================================

def main():

    print("\n")
    print("=" * 65)
    print(
        "2026 AUSTRIAN GRAND PRIX"
    )
    print(
        "PERFORMANCE ENGINEERING ANALYSIS"
    )
    print("=" * 65)

    print(
        f"\nPython executable:\n"
        f"{sys.executable}"
    )

    print(
        f"\nProject directory:\n"
        f"{PROJECT_ROOT}"
    )

    # -----------------------------------
    # Prepare directories
    # -----------------------------------
    create_directories()

    total_scripts = len(
        SCRIPTS
    )

    completed = 0
    failed = []

    total_start = time.time()

    # -----------------------------------
    # Run analysis
    # -----------------------------------
    for number, script in enumerate(
        SCRIPTS,
        start=1
    ):

        print(
            f"\nAnalysis "
            f"{number}/{total_scripts}"
        )

        success = run_script(
            script
        )

        if success:

            completed += 1

        else:

            failed.append(
                script
            )

            if STOP_ON_ERROR:

                print(
                    "\nPipeline stopped "
                    "because STOP_ON_ERROR "
                    "is enabled."
                )

                break

    # -----------------------------------
    # Total execution time
    # -----------------------------------
    total_elapsed = (
        time.time()
        - total_start
    )

    # ===================================
    # FINAL SUMMARY
    # ===================================

    print("\n")
    print("=" * 65)
    print(
        "ANALYSIS SUMMARY"
    )
    print("=" * 65)

    print(
        f"Completed: "
        f"{completed}/{total_scripts}"
    )

    print(
        f"Total execution time: "
        f"{total_elapsed:.1f} s"
    )

    if failed:

        print(
            "\nFailed scripts:"
        )

        for script in failed:

            print(
                f" - {script}"
            )

    else:

        print(
            "\nAll analysis scripts "
            "completed successfully."
        )

    print("\n")
    print("=" * 65)


# ===================================
# ENTRY POINT
# ===================================

if __name__ == "__main__":

    main()