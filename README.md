# 2026 Austrian Grand Prix — Performance Engineering Analysis

An independent Formula 1 performance-engineering investigation of George Russell (RUS) and Andrea Kimi Antonelli (ANT) at the 2026 Austrian Grand Prix, developed using Python and FastF1.

The project combines race-level statistical analysis with selected-lap telemetry investigation to examine where measurable performance differences developed, how repeatable they were, and how those observations could be translated into engineering hypotheses and controlled test objectives.

Rather than treating telemetry as a way to simply determine who was faster, the project follows a performance-engineering workflow:

> Evidence → Hypothesis → Controlled Test → Measurement → Accept / Modify / Reject


## Full Engineering Report

The complete performance-engineering investigation is provided in two parts:

### Part 1 — Introduction, Methodology and Circuit Engineering Context
[Read Report Part 1](report/mercedesaustriareportpart1.pdf)
### Part 2 — Race Performance, Telemetry Analysis and Engineering Recommendations
[Read Report Part 2](https://raw.githubusercontent.com/ssudebeyza/Mercedes-Austria-GP-engineering-analysis/main/report/mercedesaustriareportpart2.pdf)

Together, the two documents contain the complete investigation, from the research methodology and circuit context through race-level analysis, selected-lap telemetry, corner-level diagnostics, engineering recommendations and conclusions.

## Project Objective

The objective was not simply to compare final lap times or determine which driver performed better.

Instead, the investigation asks:

- Where did measurable performance differences develop?
- Were those differences race-wide or localised to particular phases?
- How repeatable was each driver's performance?
- Which differences can be directly observed in public telemetry?
- Which explanations remain hypotheses because relevant channels are unavailable?
- How could those observations be converted into controlled engineering tests?

This distinction is important because race outcome, representative pace, repeatability and local telemetry performance answer different engineering questions.

Russell won the Grand Prix and therefore achieved the stronger overall competitive outcome. Antonelli nevertheless demonstrated locally faster execution in several selected-lap areas, providing useful comparison points for engineering investigation.


## Analysis Overview

The project investigates four main levels of performance.

### Race-Level Performance

- Position evolution
- Tyre strategy
- Pit-stop timing
- Lap-time evolution
- Five-lap moving-average pace
- Representative pace distribution
- Stint performance
- Stint pace trends

### Sector-Level Performance

- Sector median comparison
- Identification of where lap-time differences were concentrated

### Selected-Lap Telemetry

- Selected representative-lap comparison
- Cumulative lap-time delta
- Corner-level performance delta
- Corner performance loss mapping
- Brake-application comparison
- Speed and throttle traces

### Detailed Corner Investigation

Detailed investigations were performed for:

- Turn 3
- Turn 6
- Turn 6–7 sequence
- Turn 9–10 sequence

The project also includes:

- Selected vs typical representative-lap comparison
- Exploratory theoretical performance envelope
- Engineering KPI export


## Key Results

### Representative Race Pace

| Metric | Russell | Antonelli |
| Mean | 71.868 s | 71.825 s |
| Median | 71.696 s | 71.723 s |
| Standard deviation | 0.893 s | 1.065 s |
| Representative laps | 64 | 65 |

Antonelli recorded a marginally lower representative mean lap time, while Russell demonstrated lower lap-time variability.

The approximately 0.04 s difference in representative mean pace should not be interpreted as evidence that Antonelli performed better overall.

Russell combined competitive pace with stronger repeatability and converted his performance into the race-winning result.


## Sector Performance

Median sector times:

| Sector | RUS | ANT | ANT − RUS |
| S1 | 17.384 s | 17.388 s | +0.004 s |
| S2 | 32.2785 s | 32.249 s | −0.0295 s |
| S3 | 22.014 s | 21.999 s | −0.015 s |

Throughout the repository:

Delta = ANT − RUS

Negative → Antonelli advantage
Positive → Russell advantage


Using one consistent sign convention prevents interpretation changes between sector, lap and corner analyses.

## Selected Representative-Lap Investigation

The detailed telemetry case study uses:

| Driver | Selected Representative Lap |
| RUS | 70.683 s |
| ANT | 70.374 s |

Selected-lap delta:

ANT − RUS = −0.309 s


These are selected representative laps, not verified absolute fastest laps.

The comparison is therefore used to investigate where the 0.309 s difference developed rather than to make a claim about overall race superiority.



## Corner-Level Performance

Selected-corner analysis produced the following approximate deltas:

| Corner | ANT − RUS | Local Advantage |
| T1 | −0.067 s | ANT |
| T3 | −0.042 s | ANT |
| T4 | +0.013 s | RUS |
| T6 | −0.145 s | ANT |
| T7 | +0.009 s | RUS |
| T9 | −0.025 s | ANT |
| T10 | −0.047 s | ANT |

These values describe performance within defined selected-lap analysis windows and are not intended to represent independent or directly additive lap-time gains.

## Turn 6 Case Study

Turn 6 produced the largest selected-corner difference:

T6 delta ≈ −0.145 s


Approximately 82% of the measured difference developed before the minimum-speed point, shifting the investigation towards the entry-to-mid-corner phase.

Minimum speeds were approximately:

| Driver | Minimum Speed |
| RUS | 161.08 km/h |
| ANT | 163.00 km/h |

Throttle-recovery indicators:

| Metric | RUS | ANT |
| D50 after minimum speed | ~30 m | ~24 m |
| D90 after minimum speed | ~70 m | ~64 m |
| Brake release → D50 | ~86 m | ~74 m |

These measurements show observable differences in the selected laps.

They do not establish that higher minimum speed or earlier throttle application independently caused the complete time difference.

Without steering angle, true brake pressure, detailed tyre state and vehicle setup information, the underlying physical mechanism cannot be uniquely identified from public telemetry.

## Turn 3 — A Useful Counterexample

Turn 3 demonstrates why individual telemetry metrics should not be interpreted in isolation.

Approximate minimum speeds:


RUS ≈ 69.0 km/h
ANT ≈ 64.4 km/h


Despite Russell carrying the higher minimum speed, Antonelli was approximately:

0.042 s faster


within the defined selected-corner analysis window.

This demonstrates that higher minimum speed does not automatically mean a faster corner. Performance must be evaluated across the complete analysed corner sequence rather than from a single KPI.

## Turn 9–10 Sequence

The selected-lap analysis showed:

T9  ≈ −0.025 s
T10 ≈ −0.047 s

Combined ≈ −0.072 s


At T10:

| Driver | Minimum Speed |
| RUS | ~161.10 km/h |
| ANT | ~164.13 km/h |

Antonelli also reached approximately 90% throttle around 10 m earlier after the minimum-speed point in the selected comparison.

Again, these are treated as associated telemetry observations rather than proof of a single causal mechanism.


## Stint Analysis

Observed stint pace slopes:

| Stint | RUS | ANT |
| 1 | +0.028 s/lap | +0.026 s/lap |
| 2 | +0.044 s/lap | +0.028 s/lap |
| 3 | +0.012 s/lap | −0.061 s/lap |

Antonelli's negative final-stint slope represents an observed improvement in lap-time trend, not physical negative tyre degradation.

Race pace is influenced by several interacting factors, including fuel reduction, traffic, track evolution and tyre condition. The trend therefore cannot be attributed to tyre degradation alone.


## Engineering Interpretation

A major aim of the project was to separate three different levels of evidence:

Observation

What is directly measurable in the available telemetry.

Engineering Hypothesis

A possible explanation consistent with those observations.

Validation

A controlled test or additional dataset required to determine whether the hypothesis is supported.

For example, the Turn 6 analysis identifies a measurable selected-lap deficit for Russell and localises most of it before minimum speed.

That evidence can justify testing a small change in corner execution.

It does not justify immediately concluding that Russell should simply carry more minimum speed.

A suitable engineering test would instead evaluate the change while monitoring both T6 performance and the combined T6–T7 sequence, ensuring that a local improvement does not create a downstream loss.


## Report Structure

The accompanying report is organised into eight chapters:

1. Introduction and Project Rationale
2. Research Methodology and Data Limitations
3. Circuit Engineering Context
4. Race Performance Analysis
5. Performance Discussion
6. Selected-Lap Telemetry Investigation
7. Engineering Recommendations and Test Planning
8. Conclusions


## Installation

Clone the repository:

```bash
git clone <repository-url>
cd austrian-gp-performance-analysis
```

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Upgrade pip and install the dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Requirements

The project uses:

fastf1>=3.6.0
pandas>=2.2.0
numpy>=1.26.0
matplotlib>=3.8.0

Python standard-library modules such as pathlib, subprocess, sys and time do not require separate installation.


## Running the Analysis

To execute the complete analysis pipeline:

```bash
python main.py
```

The main script runs the individual analyses sequentially.

Each investigation can also be executed independently. For example:

```bash
python 16_t6_analysis.py
```

or:

```bash
python 19_t9_t10_analysis.py
```


## FastF1 Cache

FastF1 data is cached locally in:

```text
cache/
```

The first run may take longer because the required session data must be downloaded.

Internet access is required when the relevant FastF1 data is not already cached.

The cache directory is excluded from Git version control.

## Data Limitations

This project uses publicly available FastF1 data rather than team-level Formula 1 telemetry.

Important unavailable or limited information includes:

- Steering angle
- True brake pressure
- Detailed tyre temperatures and pressures
- Differential settings
- Detailed aerodynamic balance
- Complete energy-management information
- Vehicle setup parameters
- High-frequency internal vehicle-state channels

The FastF1 Brake channel is therefore treated as binary brake application, not brake pressure.

Derived quantities based on numerical differentiation are also treated cautiously because telemetry sampling and interpolation can amplify noise.

For these reasons, the analysis distinguishes between measured observations and engineering hypotheses.

## Theoretical Performance Envelope

The repository includes an exploratory theoretical performance-envelope analysis.

It combines locally stronger observed time increments from the two selected representative laps to investigate the performance contained within the comparison.

It is not intended to represent:

- a perfect lap,
- a guaranteed achievable lap time,
- or a prediction that every local advantage could be combined simultaneously.

Corner interactions, vehicle state, tyre condition, setup and downstream effects mean that locally observed gains are not necessarily independent or additive.


## Tools

- Python
- FastF1
- Pandas
- NumPy
- Matplotlib


## About This Project

This project was developed as an independent motorsport engineering portfolio investigation.

My interest is in applying aerodynamics, vehicle dynamics, telemetry analysis and performance engineering to understand how measurable differences in vehicle and driver behaviour translate into lap-time performance.

The project developed from a relatively simple Formula 1 telemetry comparison into a broader engineering investigation focused on evidence quality, performance diagnosis, data limitations and controlled validation.

The central lesson from the project was that identifying a difference in telemetry is only the beginning of the engineering process.

The next questions are:

Where did it develop? What evidence supports the explanation? What information is missing? And how would I test it?