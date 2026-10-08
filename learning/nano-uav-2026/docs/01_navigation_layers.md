# Navigation is a set of connected problems

## 1. State estimation: where am I, and how am I moving?

An estimator combines observations to estimate position, orientation, velocity or other states. OpenVINS is a filter-based visual-inertial implementation; ORB-SLAM3 is a visual/visual-inertial SLAM reference. These are not trajectory planners. [S07](../sources/REFERENCES.md#s07), [S14](../sources/REFERENCES.md#s14).

For your own interface, record the reference frame, units, timestamp origin, uncertainty representation and invalid-state behaviour. An apparently smooth trajectory can still be expressed in the wrong frame.

## 2. Perception and mapping: what can I safely infer about the surroundings?

Your implementation might use a depth image, a small local obstacle representation or a larger map. Treat missing, saturated or stale sensor values as unknown, not automatically as free space. Distinguish the image used by a navigation policy from the data quality required by a scientific measurement.

Suggested design: keep a latency-sensitive navigation branch and a separately budgeted measurement/recording branch. Sharing a sensor does not eliminate synchronization, processing or bandwidth costs.

## 3. Local planning and policies: what motion should happen next?

EGO-Swarm and GCOPTER represent geometric planning/optimization references. YOPO learns a trajectory-generating mapping. NavRL learns a navigation policy with reinforcement learning. They should be compared only after aligning input information and control authority. [S08](../sources/REFERENCES.md#s08), [S09](../sources/REFERENCES.md#s09), [S06](../sources/REFERENCES.md#s06), [S12](../sources/REFERENCES.md#s12).

A candidate that receives perfect simulated state has an advantage over one using delayed onboard measurements. Report that difference rather than attributing everything to the planner.

## 4. Control: can the vehicle follow the requested motion?

For an initial integration, keep the stabilizing flight-control implementation separate from the experimental task process. Agree on whether the interface accepts positions, velocities, attitudes or something else. Define command expiration and tested takeover behaviour before connecting a planner. PX4's official offboard example is an integration reference, not a universal safety configuration. [S21](../sources/REFERENCES.md#s21).

Do not send a four-dimensional policy output to a flight controller merely because the message also has four fields. Derive the meaning, units, frame and scaling from the selected implementation.

## 5. Task decisions: where should I observe or measure next?

Environment exploration and scientific measurement selection need different objective functions. FUEL provides an exploration reference; the included next-view exercise instead models the usefulness of a scalar observation. [S10](../sources/REFERENCES.md#s10).

Suggested hierarchy: choose a task objective, propose a destination or viewpoint, validate its feasibility, then delegate motion to the navigation/control stack. Do not let a high-level language response bypass local constraints.

## 6. Active perception and next-view selection

Active perception chooses motion partly for what the sensors should observe next. Depending on the task, a useful view may improve visual-inertial tracking, reveal unknown space, inspect a target, or reduce uncertainty about a measurement. State the information objective before comparing candidate viewpoints.

Exploration and task-specific inspection are related but different objectives. FUEL is a frontier-based UAV exploration framework [S10](../sources/REFERENCES.md#s10). The Receding Horizon Next Best View Planner is a classic implementation that selects a next pose using exploration gain [S29](../sources/REFERENCES.md#s29). Its README lists ROS Indigo and Jade as tested, so treat it as an algorithm and code reference, not a current deployment recipe.

The bundled [next-view exercise](../examples/next_view.py) is a scalar-Gaussian teaching model. It discounts information gain by an assumed measurement-validity probability and subtracts a simple cost. Those values are synthetic. A real system must validate calibration and include visibility, sensor range and resolution, motion feasibility, travel time, energy, observation age, and the mission's measurement-quality objective.

## 7. Evidence and georeferencing

Local collision avoidance alone does not establish a global coordinate, a reproducible measurement location or a dock-return capability. Specify those as separate requirements. Even a policy that can operate without a conventional odometry module does not automatically provide the scientific coordinates needed by another subsystem.

## Training versus deployment

Training can use a desktop simulator while deployment runs a small fixed policy. Conversely, a small policy may rely on expensive depth production, object tracking or state estimation. Always maintain two diagrams in your own notes: the training dependencies and the onboard runtime dependencies. The methods in the next chapter are classified using this distinction.
