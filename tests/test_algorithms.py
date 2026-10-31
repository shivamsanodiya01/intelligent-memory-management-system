"""Automated checks for FIFO, LRU, Optimal, and Predictive replacement."""

import unittest

from algorithms.fifo import fifo
from algorithms.lru import lru
from algorithms.optimal import optimal
from algorithms.predictive import predictive


# Classic textbook string (Silberschatz / many OS notes).
SAMPLE = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
FRAMES = 3


class TestInputHandling(unittest.TestCase):
    def test_empty_reference_string(self):
        for runner in (fifo, lru, optimal, predictive):
            result = runner([], 3)
            self.assertIsNotNone(result["error"])
            self.assertEqual(result["page_faults"], 0)
            self.assertEqual(result["steps"], [])

    def test_zero_frames(self):
        for runner in (fifo, lru, optimal, predictive):
            result = runner([1, 2, 3], 0)
            self.assertIsNotNone(result["error"])

    def test_negative_frames(self):
        for runner in (fifo, lru, optimal, predictive):
            result = runner([1, 2, 3], -2)
            self.assertIsNotNone(result["error"])


class TestFifoLruOptimal(unittest.TestCase):
    def test_fifo_known_fault_count(self):
        result = fifo(SAMPLE, FRAMES)
        self.assertIsNone(result["error"])
        self.assertEqual(result["page_faults"], 15)
        self.assertEqual(result["page_hits"], 5)
        self.assertEqual(result["page_faults"] + result["page_hits"], len(SAMPLE))

    def test_lru_known_fault_count(self):
        result = lru(SAMPLE, FRAMES)
        self.assertIsNone(result["error"])
        self.assertEqual(result["page_faults"], 12)
        self.assertEqual(result["page_hits"], 8)

    def test_optimal_known_fault_count(self):
        result = optimal(SAMPLE, FRAMES)
        self.assertIsNone(result["error"])
        self.assertEqual(result["page_faults"], 9)
        self.assertEqual(result["page_hits"], 11)

    def test_hit_and_fault_ratios(self):
        result = fifo(SAMPLE, FRAMES)
        self.assertAlmostEqual(result["hit_ratio"], 5 / 20)
        self.assertAlmostEqual(result["fault_ratio"], 15 / 20)

    def test_every_step_is_hit_or_fault(self):
        for runner in (fifo, lru, optimal):
            result = runner(SAMPLE, FRAMES)
            self.assertEqual(len(result["steps"]), len(SAMPLE))
            for step in result["steps"]:
                self.assertIn(step["status"], ("Hit", "Fault"))
                self.assertEqual(len(step["frames"]), FRAMES)

    def test_first_unique_pages_are_faults(self):
        result = fifo([1, 2, 3], 3)
        self.assertEqual(result["page_faults"], 3)
        self.assertEqual(result["page_hits"], 0)

    def test_repeated_page_with_room_is_hit(self):
        result = lru([5, 5, 5], 2)
        self.assertEqual(result["page_faults"], 1)
        self.assertEqual(result["page_hits"], 2)


class TestPredictive(unittest.TestCase):
    def test_runs_on_sample_string(self):
        result = predictive(SAMPLE, FRAMES)
        self.assertIsNone(result["error"])
        self.assertEqual(result["algorithm"], "Predictive")
        self.assertEqual(result["page_faults"] + result["page_hits"], len(SAMPLE))
        self.assertEqual(len(result["steps"]), len(SAMPLE))

    def test_is_deterministic(self):
        first = predictive(SAMPLE, FRAMES, {"alpha": 0.4, "beta": 0.4, "gamma": 0.2})
        second = predictive(SAMPLE, FRAMES, {"alpha": 0.4, "beta": 0.4, "gamma": 0.2})
        self.assertEqual(first["page_faults"], second["page_faults"])
        self.assertEqual(
            [step["frames"] for step in first["steps"]],
            [step["frames"] for step in second["steps"]],
        )

    def test_fault_steps_include_prediction_text(self):
        result = predictive(SAMPLE, FRAMES)
        fault_with_full_memory = [
            step for step in result["steps"] if step["status"] == "Fault" and step["replaced"] != "-"
        ]
        self.assertTrue(fault_with_full_memory)
        self.assertIn("Victim", fault_with_full_memory[0]["prediction"])

    def test_does_not_use_future_references(self):
        # Same prefix must produce the same first decisions even if the tail changes.
        prefix = [1, 2, 3, 4]
        a = predictive(prefix + [1, 2], 3)
        b = predictive(prefix + [9, 8], 3)
        for step_a, step_b in zip(a["steps"][:4], b["steps"][:4]):
            self.assertEqual(step_a["frames"], step_b["frames"])
            self.assertEqual(step_a["status"], step_b["status"])
            self.assertEqual(step_a["replaced"], step_b["replaced"])


if __name__ == "__main__":
    unittest.main()
