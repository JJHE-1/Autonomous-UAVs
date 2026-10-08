"""A scalar-Gaussian next-view teaching example. No robot commands are sent.

Assumptions: x has Gaussian prior variance P; a valid observation has independent
Gaussian noise variance R. Validity is observed and is independent of x. An invalid
observation provides zero information. Therefore expected information is
p_valid * 0.5 * log(1 + P/R). Travel cost is converted to utility units with an
explicit coefficient. This is one-step selection, not full Bayesian robotics,
SLAM, collision checking or a calibration procedure. All candidates are synthetic.
"""
from __future__ import annotations
import argparse
import json
import math
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Candidate:
    name: str
    noise_variance: float
    p_valid: float
    travel_cost: float


def number(value: float, name: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'{name} must be numeric')
    value = float(value)
    if not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError(f'{name} must be finite and {"positive" if positive else "nonnegative"}')
    return value


def evaluate(candidate: Candidate, prior_variance: float = 1.0,
             cost_weight: float = 0.2) -> dict:
    prior = number(prior_variance, 'prior_variance', positive=True)
    noise = number(candidate.noise_variance, 'noise_variance', positive=True)
    probability = number(candidate.p_valid, 'p_valid')
    cost = number(candidate.travel_cost, 'travel_cost')
    weight = number(cost_weight, 'cost_weight')
    if probability > 1:
        raise ValueError('p_valid must be between 0 and 1')
    if not isinstance(candidate.name, str) or not candidate.name.strip():
        raise ValueError('candidate name must be nonempty')
    information = 0.5 * math.log1p(prior / noise)
    posterior = 1.0 / (1.0 / prior + 1.0 / noise)
    expected_information = probability * information
    utility = expected_information - weight * cost
    if not all(math.isfinite(v) for v in (information, posterior, expected_information, utility)):
        raise ValueError('inputs overflow the calculation')
    return {
        **asdict(candidate),
        'information_if_valid_nats': information,
        'posterior_variance_if_valid': posterior,
        'expected_information_nats': expected_information,
        'cost_penalty_nats': weight * cost,
        'utility': utility,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prior-variance', type=float, default=1.0)
    parser.add_argument('--cost-weight', type=float, default=0.2)
    args = parser.parse_args()
    candidates = (
        Candidate('A_precise_but_often_invalid', 0.04, 0.20, 1.0),
        Candidate('B_reliable_balanced', 0.20, 0.95, 0.4),
        Candidate('C_nearby_but_noisy', 0.60, 0.99, 0.1),
    )
    try:
        rows = [evaluate(c, args.prior_variance, args.cost_weight) for c in candidates]
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        parser.error(str(exc))
    best = max(rows, key=lambda row: row['utility'])
    print(json.dumps({
        'evidence_class': 'synthetic_teaching_example',
        'prior_variance': args.prior_variance,
        'cost_weight_nats_per_cost_unit': args.cost_weight,
        'candidates': rows,
        'best_by_information_alone': max(rows, key=lambda r: r['information_if_valid_nats'])['name'],
        'best_by_utility': best['name'],
        'warning': ('Validity probabilities are assumed, not learned or calibrated. '
                    'Selection ignores feasibility and inter-view correlations. '
                    'No control command, global position or safe trajectory is produced.'),
    }, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
