# Corrections to the original resource index

The original index remains useful as historical context. This update does not classify everything old as obsolete.

| Item | Correction or clarification | Evidence |
|---|---|---|
| `maplab` hyperlink | The original points to `mav_voxblox_planning`; use `ethz-asl/maplab`. | [S01](../sources/REFERENCES.md#s01), [S20](../sources/REFERENCES.md#s20) |
| PX4-Avoidance | Mark as archived/historical; the archive date shown is 2024-08-01. Do not present it as the default new-project starting point. | [S19](../sources/REFERENCES.md#s19) |
| PULP-Dronet | Distinguish v1, v2 and Tiny v3, including different models/toolchains. | [S02](../sources/REFERENCES.md#s02), [S03](../sources/REFERENCES.md#s03) |
| A single `ROS` checkmark | Record version, branch and example platform instead. NavRL's ROS1 and ROS2 examples are not the same robot. | [S11](../sources/REFERENCES.md#s11) |
| Optional GPU dependency | EGO's CUDA sensor renderer is not proof that the real planner itself needs that simulator GPU. | [S08](../sources/REFERENCES.md#s08) |
| Method categories | Separate state estimation, mapping, local planning, control, exploration and semantic task decisions. | [Navigation layers](01_navigation_layers.md) |
| Publication/release maturity | AutoFly's README still describes planned modules; distinguish a research announcement from a complete deployment release. | [S17](../sources/REFERENCES.md#s17) |
| `ARM` versus `MCU-ready` | An ARM-computer demonstration does not establish a microcontroller port. | [S04](../sources/REFERENCES.md#s04), [S18](../sources/REFERENCES.md#s18) |

## Changes actually applied by the optional importer

With `--update-readme`, the importer adds a short link block and replaces only the exact known maplab-link text. It saves the original README bytes inside the imported guide's `provenance/` directory first. All other legacy classifications are documented here rather than silently rewriting the original authors' descriptions.

No broad maintenance claim has been inferred from a repository's age, star count or absent release tag.
