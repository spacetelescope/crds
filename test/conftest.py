import json
from pathlib import Path

from pytest import fixture


@fixture
def combined_spec(scope='session'):
    return json.load(
        open(Path(__file__).parent.parent / "crds" / "roman" / "specs" / "combined_specs.json", 'r'))
