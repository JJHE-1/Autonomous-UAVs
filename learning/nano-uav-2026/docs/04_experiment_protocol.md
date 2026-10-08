# Edge-navigation experiment protocol

This is a proposed protocol. Set task-specific acceptance thresholds before collecting comparison results. Blank fields are unknown, not zero.

## 1. Separate four kinds of evidence

**Source statement:** what the repository or paper says.

**Editorial assessment:** why a method might be a useful candidate.

**Local measurement:** what a named build on a named machine actually produced.

**Task validation:** whether a defined mission succeeded under stated conditions.

Do not promote a source statement into a local measurement. The [source register](../sources/REFERENCES.md) and [benchmark template](../templates/benchmark.json) keep these separate.

## 2. Measure end-to-end age as well as inference time

Instrument acquisition/exposure timing, preprocessing, depth production, estimation, inference/planning, message transfer and controller consumption. Use synchronized clocks or measure their offset and uncertainty. Include buffering and scheduling; report dropped frames and maximum input age.

The educational serial approximation is:

`response_ms = sensor_ms + preprocessing_ms + compute_ms + transport_ms + actuation_wait_ms`

A real pipelined system may overlap stages. Neither summing isolated medians nor adding stage-wise 99th percentiles gives a validated end-to-end percentile. Measure timestamps across the complete path. State whether a reported time is an average, percentile, worst observed value, or analytical bound.

## 3. Account for memory and compute

Report parameter storage, runtime tensors, image/depth buffers, recurrent state, stack/heap, middleware, map storage and external-memory traffic. Include compiler version, quantization, input dimensions, batch size, CPU/NPU mapping and fallback operators. A parameter-only estimate cannot establish that a model fits the board.

Avoid converting TOPS/GOPS ratios into latency predictions across processors. Benchmark the specific model and the complete concurrent workload.

## 4. Account for power, mass and temperature

Define the measurement boundary: accelerator alone, task board, full sensing/compute subsystem, or whole aircraft. Measure mean and peak power at that boundary. Record camera, compute module, memory, regulator, storage, cabling, mounts and cooling mass. Do not compare a neural-engine power number with an entire companion board.

Measure thermal throttling and supply stability while the intended sensors and logging are active. Separate propulsion energy from sensing/compute energy when interpreting endurance changes.

## 5. Use paired, controlled tasks

Use the same obstacle geometry, start/goal, sensor observability, velocity limits and evaluation policy where possible. Split training and evaluation scenes. Save seeds and per-trial logs, not only a best video. Count interventions and early aborts; do not remove them from success-rate denominators without explanation.

Report collision count, minimum observed clearance, completion time, path length, state-estimation error where ground truth exists, and the mission's measurement-quality metric. Coverage of a map is not the same as informative or repeatable sensing.

## 6. Test degradation deliberately before target deployment

Test thin obstacles before and after input resizing; missing depth; changes in illumination; motion blur; viewpoint changes; unexpected moving objects; frame loss; clock drift; state-estimation degradation; compute overload; communications loss; and task-process restart.

Missing depth is not evidence of free space. A low-resolution observation that omits a thin branch cannot be fixed merely by making policy inference faster. Treat these as experiment design concerns, not as claims that every listed method necessarily fails in such a scene.

## 7. Keep the braking example in its proper role

The bundled calculator uses `distance = speed * delay + speed**2 / (2 * deceleration) + margin`. It assumes one-dimensional constant deceleration after a fixed delay and a stationary obstacle. It omits control transients, wind, jerk, localization error, geometry and dynamic obstacles. It is a teaching calculation, not a flight-clearance guarantee.

A flight envelope requires independently measured dynamics and sensing limits, with uncertainties and failure handling appropriate to the actual platform.

## 8. Report deployment honestly

A deployment report must include its code revision, firmware revision, configuration, sensor calibration, environment, device type and raw logs. Label a simulator result as simulation, a desktop inference result as desktop, and an operator conversion report as conversion. None alone establishes board-level or closed-loop flight performance.
