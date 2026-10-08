"""Tests for educational arithmetic only, not navigation or flight validation."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

budget = load('edge_budget_under_test', 'examples/edge_budget.py')
view = load('next_view_under_test', 'examples/next_view.py')

class BudgetTests(unittest.TestCase):
    def test_parameter_count(self):
        self.assertEqual(sum(budget.parameter_breakdown().values()), 513920)

    def test_parameter_dimension_change(self):
        self.assertEqual(sum(budget.parameter_breakdown(10, 4).values()) - 513920, 192)

    def test_storage(self):
        result = budget.estimate_budget(513920, 8, {'one': 73}, .5, 1, .15)
        self.assertEqual(result['ideal_parameter_bytes'], 513920)
        self.assertAlmostEqual(result['simplified_distance_m'], .3115)
        self.assertIsNone(result['peak_runtime_ram_bytes'])
        self.assertFalse(result['board_fit_verified'])

    def test_fp32_storage(self):
        result = budget.estimate_budget(513920, 32, {'one': 0}, 0, 1, 0)
        self.assertEqual(result['ideal_parameter_bytes'], 2055680)

    def test_invalid_input(self):
        for value in (-1, float('nan'), float('inf'), True, '5'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                budget.estimate_budget(100, 8, {'one': value}, .5, 1, 0)

    def test_zero_deceleration(self):
        with self.assertRaises(ValueError):
            budget.estimate_budget(100, 8, {'one': 1}, .5, 0, 0)

    def test_invalid_parameters(self):
        for params in (0, -1, True, 2.5):
            with self.subTest(params=params), self.assertRaises(ValueError):
                budget.estimate_budget(params, 8, {'one': 1}, .5, 1, 0)

    def test_empty_stages(self):
        with self.assertRaises(ValueError):
            budget.estimate_budget(1, 8, {}, 1, 1, 0)

class NextViewTests(unittest.TestCase):
    def test_posterior_variance(self):
        row = view.evaluate(view.Candidate('x', 1, 1, 0), 1, 0)
        self.assertAlmostEqual(row['posterior_variance_if_valid'], .5)

    def test_zero_validity(self):
        row = view.evaluate(view.Candidate('x', .1, 0, 2), 1, .2)
        self.assertEqual(row['expected_information_nats'], 0)
        self.assertAlmostEqual(row['utility'], -.4)

    def test_quality_changes_selection(self):
        a = view.evaluate(view.Candidate('a', .04, .20, 1))
        b = view.evaluate(view.Candidate('b', .20, .95, .4))
        self.assertGreater(a['information_if_valid_nats'], b['information_if_valid_nats'])
        self.assertGreater(b['utility'], a['utility'])

    def test_invalid_probability(self):
        for p in (-.1, 1.1, float('nan'), True):
            with self.subTest(p=p), self.assertRaises(ValueError):
                view.evaluate(view.Candidate('x', 1, p, 0))

    def test_invalid_variance(self):
        with self.assertRaises(ValueError):
            view.evaluate(view.Candidate('x', 0, 1, 0))

    def test_negative_cost(self):
        with self.assertRaises(ValueError):
            view.evaluate(view.Candidate('x', 1, 1, -1))

if __name__ == '__main__':
    unittest.main()
