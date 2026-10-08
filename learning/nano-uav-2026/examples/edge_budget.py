"""Educational storage/latency arithmetic. Not flight-control or safety software.

Default layer dimensions are independently transcribed as numbers from the
DiffPhysDrone model definition, reviewed 2026-10-08. No upstream implementation
or trained weights are included. See sources/REFERENCES.md, S05.
All default timings and motion assumptions below are synthetic.
"""
from __future__ import annotations
import argparse
import json
import math
from collections.abc import Mapping


def finite_number(value: float, name: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'{name} must be a number, not a boolean or string')
    value = float(value)
    if not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError(f'{name} must be finite and {"positive" if positive else "nonnegative"}')
    return value


def positive_integer(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f'{name} must be a positive integer')
    return value


def parameter_breakdown(obs_dim: int = 9, action_dim: int = 4) -> dict[str, int]:
    """Count weights and biases from documented dimensions, without PyTorch."""
    positive_integer(obs_dim, 'obs_dim')
    positive_integer(action_dim, 'action_dim')
    hidden = 192
    return {
        'conv_1': 1 * 32 * 2 * 2,
        'conv_2': 32 * 64 * 3 * 3,
        'conv_3': 64 * 128 * 3 * 3,
        'image_projection': (128 * 2 * 4) * hidden,
        'observation_projection_with_bias': obs_dim * hidden + hidden,
        'gru_input_and_hidden_weights': 3 * hidden * hidden * 2,
        'gru_two_bias_vectors': 3 * hidden * 2,
        'action_projection': hidden * action_dim,
    }


def estimate_budget(params: int, bits: int, stages_ms: Mapping[str, float],
                    speed_mps: float, deceleration_mps2: float,
                    margin_m: float) -> dict:
    positive_integer(params, 'params')
    if isinstance(bits, bool) or not isinstance(bits, int) or bits not in (8, 16, 32):
        raise ValueError('bits must be one of 8, 16 or 32')
    if not isinstance(stages_ms, Mapping) or not stages_ms:
        raise ValueError('stages_ms must be a nonempty mapping')
    checked = {str(k): finite_number(v, str(k)) for k, v in stages_ms.items()}
    speed = finite_number(speed_mps, 'speed_mps')
    decel = finite_number(deceleration_mps2, 'deceleration_mps2', positive=True)
    margin = finite_number(margin_m, 'margin_m')
    latency_ms = sum(checked.values())
    distance_m = speed * latency_ms / 1000.0 + speed * speed / (2.0 * decel) + margin
    if not math.isfinite(latency_ms) or not math.isfinite(distance_m):
        raise ValueError('inputs overflow the calculation')
    weight_bytes = params * bits // 8
    return {
        'evidence_class': 'educational_calculation_not_measurement',
        'parameters': params,
        'bits_per_parameter': bits,
        'ideal_parameter_bytes': weight_bytes,
        'ideal_parameter_MiB': weight_bytes / (1024 * 1024),
        'stage_assumptions_ms': checked,
        'serial_response_assumption_ms': latency_ms,
        'speed_assumption_mps': speed,
        'deceleration_assumption_mps2': decel,
        'margin_assumption_m': margin,
        'simplified_distance_m': distance_m,
        'peak_runtime_ram_bytes': None,
        'board_fit_verified': False,
        'warning': ('No exported model or board was tested. Parameters exclude activation/runtime '
                    'memory. Timings are synthetic; pipelining is omitted. The distance assumes '
                    'fixed delay and constant 1D deceleration toward a static obstacle; '
                    'it is not a safe-flight clearance or a verified speed limit.'),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--params', type=int, default=sum(parameter_breakdown().values()))
    parser.add_argument('--bits', type=int, choices=(8, 16, 32), default=8)
    parser.add_argument('--sensor-ms', type=float, default=30.0)
    parser.add_argument('--preprocess-ms', type=float, default=8.0)
    parser.add_argument('--compute-ms', type=float, default=20.0)
    parser.add_argument('--transport-ms', type=float, default=5.0)
    parser.add_argument('--actuation-ms', type=float, default=10.0)
    parser.add_argument('--speed-mps', type=float, default=0.5)
    parser.add_argument('--deceleration-mps2', type=float, default=1.0)
    parser.add_argument('--margin-m', type=float, default=0.15)
    args = parser.parse_args()
    stages = dict(sensor=args.sensor_ms, preprocessing=args.preprocess_ms,
                  compute=args.compute_ms, transport=args.transport_ms,
                  actuation_wait=args.actuation_ms)
    try:
        result = estimate_budget(args.params, args.bits, stages, args.speed_mps,
                                 args.deceleration_mps2, args.margin_m)
    except ValueError as exc:
        parser.error(str(exc))
    result['default_architecture_parameter_breakdown'] = parameter_breakdown()
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
