import os
from pathlib import Path

import pytest


@pytest.mark.roman
def test_photom_rmap_exists():
    assert os.path.exists(Path(__file__).parents[3] / "crds" / "roman" / "specs" / "wfi_photom.rmap")


def pytest_test_photom_tpn_exist():
    assert os.path.exists(Path(__file__).parents[3] / "crds" / "roman" / "tpns" / "wfi_photom.tpn")


@pytest.mark.roman
def test_photom_tpn_headers_match_spec():
    """
    TODO: get spec headers from authoritative source
    """
    expected_headers = [
        'ROMAN.META.INSTRUMENT.DETECTOR'
    ]
    with open(Path(__file__).parents[3] / "crds" / "roman" / "tpns" / "wfi_photom.tpn", 'r') as photom_tpn:
        lines = [line.replace('\n', '') for line in photom_tpn.readlines()]

        headers = [s[:s.index(" ")] for s in filter(
            lambda l: l != '' and l[0] != '#',
            lines
        )]
        assert expected_headers == headers


@pytest.mark.roman
def test_photom_key_in_combined_spec(combined_spec):
    assert 'photom' in combined_spec['wfi']
