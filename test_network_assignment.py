"""Verify network assignment can restore matches from normalized source rows."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import assign_networks


class NetworkAssignmentTest(unittest.TestCase):
    """Exercise CSV loading and generated provider output together."""

    def test_named_emirate_restores_empty_plan_and_rerun_is_stable(self) -> None:
        """Match Dubai to DXB and recover an empty subset from the registry."""
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            networks = root / 'networks'
            networks.mkdir()
            (networks / 'Example.csv').write_text(
                'PROVIDER NAME,EMIRATE,TELEPHONE\nExample Clinic,Dubai,\n', encoding='utf-8')
            registry = [{'Index': 1, 'P': 'DXB', 'PROVIDER NAME': 'Example Clinic',
                         'lat': 25.2, 'lon': 55.3, 'TELEPHONE': ''}]
            plans = [{'id': 'example', 'name': 'Example', 'insurer': 'Example',
                      'emirates': ['DXB'], 'file': 'data/example.json', 'providers': 0}]
            for name, records in [('moh-complete', registry), ('plans', plans), ('example', [])]:
                (root / 'data' / f'{name}.json').write_text(json.dumps(records), encoding='utf-8')
            with patch.object(assign_networks, 'ROOT', str(root)), \
                    patch.object(assign_networks, 'NETWORKS_DIR', str(networks)), \
                    contextlib.redirect_stdout(io.StringIO()):
                assign_networks.main()
                first = (root / 'data/example.json').read_text()
                self.assertEqual(json.loads(first), registry)
                assign_networks.main()
                self.assertEqual((root / 'data/example.json').read_text(), first)
            metadata = json.loads((root / 'data/plans.json').read_text())[0]
            self.assertEqual(metadata['network_source'], 'official')
            self.assertEqual(metadata['providers'], 1)
