# A staged learning and reproduction route

Complete one gate at a time. This plan proposes experiments; it does not report completed external reproductions.

| Gate | Work | Evidence to save before progressing |
|---|---|---|
| 0: Interface literacy | Classify estimation, sensing, planning, control and task-selection modules. | An input/output table including frames, units and timestamps. |
| 1: Offline exercises | Run the two bundled examples and alter their assumptions. | Output JSON plus an explanation of what changed and what was omitted. |
| 2: Source and environment audit | Choose one upstream revision and inspect dependencies and model availability. | Commit SHA, submodule SHAs, exact tool versions and a clean environment description. |
| 3: Recorded-input replay | Run the chosen method on fixed sensor recordings before connecting a vehicle. | Inputs, outputs, preprocessing, checksums and failure examples. |
| 4: Simulation | Test the same task and observation quality across selected methods. | Seeds, sensor/dynamics assumptions, raw logs and failure counts. |
| 5: Propeller-off board test | Profile the deployed workload under concurrent sensing and logging. | Peak RAM, timing distribution, rail power, thermal behaviour and output agreement. |
| 6: Controlled flight | Use a cleared test area, supervision and tested recovery behaviour. | Trial definitions, interventions, collisions, near misses and sensor-quality logs. |
| 7: Target-task validation | Add the mission's measurement and coordinate requirements. | Measurement quality, alignment, return/docking results and repeatability. |

## Choose one initial route

**GAP8 route:** Tiny-PULP-Dronet source/model audit, recorded-frame comparison, then board inference. Do not flash an existing research aircraft merely to match an old tutorial. Keep a recoverable firmware baseline and test the changes separately.

**MCU/NPU route:** begin with model export and operator mapping. Compare recurrent-state handling, numerical agreement and memory layout before changing input resolution or training another policy.

**Linux companion route:** establish the required sensor/state interfaces, then test one planner with fixed replay data. Add VIO and live depth only after basic interface tests pass.

These routes are recommendations based on the [method matrix](02_methods_and_edge_fit.md), not pre-integrated distributions.

## Keep source checkouts separate

Clone selected dependencies outside this learning guide. The following only retrieves public source; it does not build or launch a flight system:

```bash
git clone --recurse-submodules https://github.com/pulp-platform/pulp-dronet.git external-pulp-dronet
git -C external-pulp-dronet rev-parse HEAD
git -C external-pulp-dronet submodule status --recursive
```

Use the selected upstream README for dependency versions and local build steps. [S03](../sources/REFERENCES.md#s03). Record the full commit SHA in [the experiment template](../templates/experiment_report.md). Do not use a file-content blob SHA as a checkout revision.

## PX4 and ArduPilot comparisons

Use each firmware's own documented simulator/integration path: [PX4 reference](../sources/REFERENCES.md#s21) and [ArduPilot SITL reference](../sources/REFERENCES.md#s22). Pin a version for each; do not mix a development-branch tutorial with an unrelated firmware binary.

Start with matched task geometry, sensor rates, mass/inertia assumptions and controller command semantics. Keep the navigation algorithm fixed when comparing flight stacks. Then keep the flight stack fixed when comparing planners. Otherwise several variables change at once and the comparison cannot identify a cause.

EGO-Swarm's default demo may directly convert commands to odometry rather than simulate full dynamics. Enabling a visible demo is therefore not equivalent to validating trajectory tracking. [S08](../sources/REFERENCES.md#s08).

## Stop conditions for development

Stop a run when inputs are stale or invalid, state estimates are unavailable, time synchronization breaks, output semantics are unknown or resource use exceeds the predeclared budget. Choose the actual recovery behaviour using the available state and tested controller capabilities. "Hover" and "return home" are not valid universal fallbacks when their required localization has failed.

## Suggested first deliverable

A reproducible recorded-input benchmark for one candidate, with version pins and an honest list of missing interfaces. Avoid starting by porting three entire navigation frameworks in parallel.
