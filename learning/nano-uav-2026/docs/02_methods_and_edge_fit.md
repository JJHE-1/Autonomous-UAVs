# Methods and nano-edge fit

**Review date: 2026-10-08. All local hardware-validation fields remain unverified.**

A resource tier is an editorial assessment. It is not a certification, a minimum system requirement, or a statement that a particular board is incapable of implementing a related idea.

## Evidence-based shortlist

| Method | Function | Evidence observed in the source | Editorial role |
|---|---|---|---|
| Tiny-PULP-Dronet v3 | Reactive visual policy | AI-deck/GAP8 deployment material and pretrained models; deployment guide specifies GAP SDK 3.9.1 and Crazyflie firmware 2022.01. [S02](../sources/REFERENCES.md#s02), [S03](../sources/REFERENCES.md#s03) | First study for existing GAP8 hardware. |
| DiffPhysDrone | Policy trained through differentiable physics | Authors report a depth-camera/ARM-computer implementation; the public model includes a GRU. [S04](../sources/REFERENCES.md#s04), [S05](../sources/REFERENCES.md#s05) | MCU/NPU port candidate, not a verified STM32N6 port. |
| YOPO | Learned trajectory generation | README reports roughly 20 ms for an INT8 ResNet-14 variant on RK3566, while the RKNN deployment update is still described as forthcoming. It requires depth and odometry inputs. [S06](../sources/REFERENCES.md#s06) | Small Linux/NPU companion candidate. |
| OpenVINS | Visual-inertial state estimation | Sparse-feature filtering with ROS-free build support. [S07](../sources/REFERENCES.md#s07) | Modular Linux reference; ROS-free does not mean MCU-ready. |
| EGO-Swarm | Geometric local trajectory planning | Single/multi-agent planner; ROS2 branch exists. Its optional CUDA code renders simulated sensing. [S08](../sources/REFERENCES.md#s08) | Baseline planner on a validation platform. |
| GCOPTER / MINCO | Trajectory representation and optimization | Optimizer implementation, not a complete perception/navigation stack. [S09](../sources/REFERENCES.md#s09) | Learn trajectory mathematics independently. |
| FUEL | Autonomous exploration | Frontier-based exploration framework. [S10](../sources/REFERENCES.md#s10) | Classic exploration comparison, not a new 2026 method. |
| NavRL | RL navigation plus safety processing | Physical tests use Jetson Orin NX, a D435i and LiDAR-inertial odometry. [S12](../sources/REFERENCES.md#s12) | Research baseline; budget the whole pipeline. |
| SUPER | Safety-aware navigation/planning | ROS1 is the primary supported version; ROS2 remains under development in the reviewed README. [S13](../sources/REFERENCES.md#s13) | Study planning and safety assumptions, not a direct MCU installation. |
| ORB-SLAM3 | Visual/visual-inertial SLAM | Public SLAM implementation. [S14](../sources/REFERENCES.md#s14) | State-estimation comparison on a suitable companion. |
| FAST-LIVO2 | LiDAR-inertial-visual odometry | LiDAR participates in the sensor configuration. [S15](../sources/REFERENCES.md#s15) | Include the sensor assembly before judging nano fit. |
| Fly0 | Semantic target grounding plus geometry | Model-service interfaces and separate geometric planning. [S16](../sources/REFERENCES.md#s16) | High-level architecture reference. |
| AutoFly-VLA | Vision-language-action research | README still lists planned training/evaluation releases and describes a remote inference server. [S17](../sources/REFERENCES.md#s17) | Reading watchlist; not an onboard MCU deployment package. |

## What to investigate for each resource tier

### Existing GAP8 / AI-deck

Start with one model variant and its prescribed toolchain. Record the checkpoint, quantization configuration, firmware tag and camera settings before changing any component. Do not attribute the fastest reported variant's performance to all variants. Model throughput is not camera-to-motion latency.

Proposed first goal: reproduce a recorded-frame output and then a propeller-off board inference. Mission location, reliable return and three-dimensional measurement alignment require separate tests.

### NPU-equipped MCU

The default DiffPhysDrone architecture inspected in [S05](../sources/REFERENCES.md#s05) has **513,920 parameters**, calculated from the layer dimensions. Ideal packed INT8 parameters occupy **513,920 bytes**, or about **0.490 MiB**. FP32 parameter storage is about **1.960 MiB**. This is arithmetic, not an exported model or a measured peak-memory result.

The model's comments describe a 12-by-16 depth input. That makes thin-obstacle preservation after preprocessing a relevant test. The GRU also makes operator support, state handling and CPU fallback important porting questions. No exported N6 model has been built for this guide.

ST lists 4.2 Mbytes of embedded RAM and distinguishes NPU-equipped AI devices from general-purpose members of the N6 family. Select the exact device. Available application RAM is not the same as a product-page total. [S18](../sources/REFERENCES.md#s18).

Proposed first goal: export one fixed configuration, inspect the compiler report and compare outputs against a reference on identical recorded inputs. A successful conversion is only the start of validation.

### Linux / RK-class companion

Treat YOPO as a candidate workload. Select either the documented paper-aligned branch or a newer experimental branch and record which one was used. The README points to a separate YOPO-MINCO branch; results must not be silently transferred between them. [S06](../sources/REFERENCES.md#s06).

Measure camera acquisition, depth generation, preprocessing, odometry, policy/planning, transport and scheduling. Evaluate memory bandwidth and thermal behaviour while logging data. Removing a development board's unused connectors does not remove the processor's memory and power requirements.

### Full-system research references

Do not reject geometry because it is not learned, or accept an RL system because its final actor is small. Compare total workloads and achievable task quality. NavRL's perception and safety dependencies are part of its implementation, and its ROS2 example uses a different robot from the ROS1 quadrotor example. [S11](../sources/REFERENCES.md#s11).

A proposed OpenVINS-plus-EGO integration remains a proposal until sensor calibration, frames, timing and controller interfaces have been checked together.

## Conditions for promotion to a flight candidate

Require repeatable inference, bounded resource use, input-quality checks, valid control semantics and tested failure handling. Retain manual supervision and an independent takeover path during experimental integration. Claims about robustness must name the tested environment and failure cases; the word "safety" in a project title is not a universal guarantee.
