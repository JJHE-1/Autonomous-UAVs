# Autonomous UAVs: Navigation and Nano-Edge Learning Guide

**English edition | Source review: 8 October 2026 | Documentation and educational examples**

A focused learning update for the [original Autonomous-UAVs index](https://github.com/alexkoven/Autonomous-UAVs). It explains how navigation methods fit together, which are plausible on small edge computers, and what must be measured before moving to a nano-UAV. This is not an integrated flight stack, a collection of vendor firmware, or a claim that the listed systems have been reproduced locally.

## Start here

Read [the learning route](docs/00_start_here.md), then [navigation layers](docs/01_navigation_layers.md). Use the [method and edge-fit matrix](docs/02_methods_and_edge_fit.md) to choose one baseline. Follow the [staged reproduction plan](docs/03_learning_path.md) and [experiment protocol](docs/04_experiment_protocol.md) before any flight integration.

| Resource constraint | Suggested first study | What this recommendation does not mean |
|---|---|---|
| Existing GAP8 / AI-deck | Tiny-PULP-Dronet v3 | Local avoidance is not precise waypoint navigation. |
| NPU-equipped MCU candidate | DiffPhysDrone policy assessment | No STM32N6 port is claimed. |
| Small Linux / RK-class companion | YOPO assessment | A network timing does not include sensing and odometry. |
| Larger validation platform | OpenVINS plus an EGO-style local planner | The combination is an integration proposal, not a verified package. |
| High-level semantic tasks | Fly0 architecture study | A remote model is not an onboard safety loop. |

These are **editorial selections**, not a ranking from a common benchmark. Evidence and limitations are linked in the method matrix.

## Run the included exercises

Python **3.10 or newer** and the standard library are sufficient. These examples use no network, GPU, ROS, model weights or flight hardware.

```bash
python examples/edge_budget.py
python examples/next_view.py
python -m unittest discover -s tests -v
python tools/validate_bundle.py
```

The first example computes parameter storage and a simplified latency/braking budget. The second shows how measurement validity and travel cost can change an information-based next-view choice. Every default value is explicitly labelled as a teaching assumption or source-derived arithmetic, not a board measurement.

## Contents

| File | Purpose |
|---|---|
| [Start here](docs/00_start_here.md) | A short route through the material |
| [Navigation layers](docs/01_navigation_layers.md) | Estimation, perception, planning, control, task decisions and active perception |
| [Method matrix](docs/02_methods_and_edge_fit.md) | 13 method entries, hardware implications and evidence boundaries |
| [Learning path](docs/03_learning_path.md) | Reading, replay, simulation and board-level gates |
| [Experiment protocol](docs/04_experiment_protocol.md) | Timing, memory, power, safety and failure reporting |
| [Reading indexes](docs/05_reading_indexes.md) | Four complementary public resource lists |
| [Upstream corrections](docs/06_upstream_corrections.md) | Link fixes, legacy labels and classification corrections |
| [Source register](sources/REFERENCES.md) | Traceable references and available file-content fingerprints |
| [Benchmark template](templates/benchmark.json) | Empty fields for actual results; unknown values stay null |
| [Upload instructions](UPLOAD.md) | Safe import into an existing fork and an explicit user-run upload |
| [Review status](REVIEW_STATUS.md) | Exactly what was and was not checked |

## Preservation and scope

The importer adds this guide under `learning/nano-uav-2026/`. Existing files are not silently replaced. With `--update-readme`, it backs up the existing root README, adds a navigation link, and corrects the exact known `maplab` hyperlink only when that exact text is present. Without that flag, the root README is untouched. It never commits, pushes, changes repository visibility or contacts GitHub.

No third-party papers, weights, datasets or source trees are bundled. Follow the upstream licenses when downloading them. See [NOTICE.md](NOTICE.md).
