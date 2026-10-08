# Start here

## The three questions to answer before choosing a repository

**What is the task?** Avoiding an obstacle, reaching a coordinate, returning to a dock, and selecting a useful scientific measurement are different tasks. Write one success condition and one failure condition for the first experiment.

**What is actually onboard?** Inventory the flight controller, processor, memory, camera, depth-generation method, range sensors, power supply, storage, wiring and cooling. Count the whole assembly. In this guide, MCU-class and Linux-companion-class describe resource constraints, not formal aircraft weight categories.

**What evidence would change the design?** Decide which measured latency, memory limit, sensor failure, or task error would reject a candidate. A successful import or compilation does not answer any of these questions.

## Recommended order

1. Read [navigation layers](01_navigation_layers.md) and classify five methods by their inputs and outputs.
2. Read [the method matrix](02_methods_and_edge_fit.md); choose one reference and at most one challenger.
3. Run the two exercises from the repository root. Change one assumption at a time.
4. Follow [the learning path](03_learning_path.md), saving one report per completed gate.

## First exercise: a fast network can still produce a slow response

Run `python examples/edge_budget.py`. The default model parameter count is independently calculated from a public architecture, while the example timing and motion values are synthetic. Increase sensing delay without changing inference time. Then double speed. Observe that parameter storage, response age and stopping-distance assumptions are different quantities.

Do not interpret the printed distance as permission to fly at that speed. The toy model omits actuator transients, jerk limits, wind, vehicle geometry, estimation error and dynamic obstacles.

## Second exercise: the best-looking viewpoint may be a poor measurement

Run `python examples/next_view.py`. One candidate offers low observation noise but has a low assumed probability of producing a valid measurement. Compare information gain alone with information gain weighted by validity and reduced by cost. Set validity to zero and examine the result.

The example is an original scalar-Gaussian teaching model, not an implementation of FUEL, RL or a real inspection controller. Its assumptions are stated in the script. A neural-network confidence score must not be inserted as a validity probability without calibration and validation.

## A useful completion note

After each exercise, write: "I changed X; Y changed; Z was not modelled; my next measurement should test W." That is more informative than a screenshot of a running terminal.
