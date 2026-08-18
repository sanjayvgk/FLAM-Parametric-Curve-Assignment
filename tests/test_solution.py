import os
import tempfile
import unittest
from pathlib import Path

import numpy as np

import solution


class SolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x, cls.y = solution.load_data()
        cls.clean = (np.pi / 6, 0.03, 55.0)

    def test_supplied_data_has_1500_valid_observations(self):
        self.assertEqual((len(self.x), len(self.y)), (1500, 1500))
        self.assertTrue(np.isfinite(self.x).all() and np.isfinite(self.y).all())

    def test_clean_parameters_have_small_residuals(self):
        metrics = solution.residual_metrics(solution.residuals(self.clean, self.x, self.y))
        self.assertLess(metrics["mean_absolute"], 2e-5)
        self.assertLess(metrics["maximum_absolute"], 5e-5)

    def test_every_inferred_t_is_in_open_domain(self):
        t, _ = solution.inverse_transform(self.x, self.y, self.clean[0], self.clean[2])
        self.assertTrue(np.all((t > 6) & (t < 60)))

    def test_known_fit_rounds_to_clean_submission(self):
        fitted = (np.deg2rad(29.9999730015), 0.0299999971, 54.9999983399)
        self.assertEqual(solution.derive_submission_parameters(fitted), self.clean)

    def test_identical_curve_has_zero_uniform_l1(self):
        self.assertEqual(solution.uniform_curve_l1(self.clean, self.clean), 0.0)

    def test_default_data_path_from_another_working_directory(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                x, y = solution.load_data()
            finally:
                os.chdir(previous)
        self.assertEqual((len(x), len(y)), (1500, 1500))


if __name__ == "__main__":
    unittest.main()
