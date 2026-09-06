"""Check that an unfinished build cannot pass release validation."""

import unittest
from unittest.mock import patch

from validate_data import validate_plan


class BuildCompletionTest(unittest.TestCase):
    """Require assignment metadata for every selectable plan."""

    def test_plan_requires_completed_network_assignment(self) -> None:
        """Reject the metadata emitted before assign_networks.py runs."""
        plan = {
            "id": "example", "name": "Example", "insurer": "Example",
            "coverage": "Both", "emirates": ["DXB"],
            "file": "data/example.json", "providers": 0,
        }
        errors: list[str] = []
        with patch("validate_data.load_json", return_value=[]):
            validate_plan(plan, errors)
        self.assertTrue(any("network_source" in error for error in errors))
        plan.update(network_source="official", layers={"official": 0})
        errors = []
        with patch("validate_data.load_json", return_value=[]):
            validate_plan(plan, errors)
        self.assertEqual(errors, [])
