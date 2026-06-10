#!/usr/bin/env python3

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "aggregate_reliability.py"
FIXTURE = ROOT / "tests" / "fixtures" / "philosophy-reliability.json"

spec = importlib.util.spec_from_file_location("aggregate_reliability", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class AggregateReliabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = module.aggregate(json.loads(FIXTURE.read_text()))
        cls.clusters = {
            row["cluster_id"]: row for row in cls.result["clusters"]
        }

    def test_core_clusters_are_reproduced(self):
        self.assertEqual(self.clusters["A-core"]["tier"], "Core")
        self.assertEqual(self.clusters["B-core"]["tier"], "Core")
        self.assertEqual(self.clusters["C-core"]["tier"], "Core")
        self.assertEqual(self.clusters["D-core"]["tier"], "Core")
        self.assertEqual(self.clusters["A-core"]["unit_support"], 1.0)

    def test_secondary_cluster_is_supported_at_threshold(self):
        self.assertEqual(self.clusters["B-silence"]["tier"], "Supported")
        self.assertEqual(self.clusters["B-silence"]["unit_support"], 0.5)

    def test_vector_agreement_exposes_disagreement(self):
        self.assertAlmostEqual(
            self.clusters["C-core"]["vector_agreement"]["reversibility"], 5 / 6
        )
        self.assertEqual(
            self.clusters["C-core"]["vector_agreement"]["impact"], 1.0
        )

    def test_minority_cluster_is_contested(self):
        self.assertEqual(self.clusters["C-composition"]["tier"], "Contested")
        self.assertAlmostEqual(
            self.clusters["C-composition"]["unit_support"], 1 / 3
        )

    def test_scenario_convergence_is_per_run(self):
        self.assertEqual(
            self.result["scenario_convergence"], {"unanimous": 2, "total": 4}
        )

    def test_verdict_uses_core_and_supported_clusters(self):
        self.assertEqual(self.result["verdict"], "Not implementable")
        self.assertEqual(self.clusters["A-core"]["severity"], "Critical")


if __name__ == "__main__":
    unittest.main()
