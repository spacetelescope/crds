import json
from pathlib import Path

import pytest


@pytest.fixture
def combined_spec(scope='session'):
    filename = Path(__file__).parent.parent / "crds" / "roman" / "specs" / "combined_specs.json"
    with open(filename, 'r') as specs_file:
        return json.load(specs_file)
